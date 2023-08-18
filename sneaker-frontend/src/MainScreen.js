import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

import { HTML5Backend } from 'react-dnd-html5-backend';
import { DndProvider, useDrag, useDrop } from 'react-dnd';

const URL = 'http://localhost:8000/';


function MainScreen() {
    const [users, setUsers] = useState([]);
    const [portfolio, setPortfolio] = useState([]);
    const [selectedUserId, setSelectedUserId] = useState(localStorage.getItem('userId') || '1');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedShoe, setSelectedShoe] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
    const [selectedSize, setSelectedSize] = useState('');
    const [isSizeModalOpen, setIsSizeModalOpen] = useState(false);



    axios.defaults.headers['ngrok-skip-browser-warning'] = 'true';

    const showSizeModal = (shoe) => {
        setSelectedShoe(shoe);
        setIsSizeModalOpen(true);
    }

    useEffect(() => {

        axios.get(URL + 'users').then(response => {
            setUsers(response.data);
            handleUserClick(selectedUserId);
        });
    }, []);

    const handleSearch = () => {
        axios.get(URL + 'search/name/' + searchTerm, { name: searchTerm }).then(response => {
            setSearchResults(response.data);
        });
    };


    const handleUserClick = (userId) => {
        setSelectedUserId(userId);
        localStorage.setItem('userId', userId);
        axios.defaults.headers['X-User-ID'] = userId;

        axios.get(URL + `user/${userId}/portfolio`).then(response => {
            setPortfolio(response.data);
        });
    };

    const handleShoeClick = (shoe) => {
        setSelectedShoe(shoe);
        setIsModalOpen(true);
    }



    const addShoeToPortfolio = () => {
        if (!selectedSize) {
            alert('Please select a size before adding to the portfolio.');
            return;
        }

        axios.post(URL + 'user/addToPortfolio', {
            userId: selectedUserId,
            shoeTitle: selectedShoe.title,
            shoeSize: selectedSize
        })
            .then(response => {
                if (response.status !== 200) {
                    alert('Failed to add shoe to portfolio. Please try again.');
                }

                setIsSizeModalOpen(false);
                setIsSearchModalOpen(false);
                handleUserClick(selectedUserId);
            })
            .catch(error => {
                alert('An error occurred. Please try again later.');
                console.error('There was an error adding the shoe to the portfolio:', error);
            });
    }

    const handleShoeDelete = () => {
        if (!window.confirm("Are you sure you want to delete this shoe from your portfolio?")) {
            return;
        }
        axios.delete(URL + `user/${selectedUserId}/portfolio/${selectedShoe.urlKey}`)
            .then(response => {
                setIsModalOpen(false);
                handleUserClick(selectedUserId);
            })
            .catch(error => {
                alert("Error removing shoe from portfolio");
                console.error("Error:", error);
            });
    }



    const DraggableShoeCard = ({ shoe, index, moveShoe }) => {
        const [{ isDragging }, dragRef] = useDrag({
            type: 'SHOE',
            item: { index },
            collect: monitor => ({
                isDragging: !!monitor.isDragging()
            })
        });

        const [, dropRef] = useDrop({
            accept: 'SHOE',
            hover: (draggedItem) => {
                if (draggedItem.index !== index) {
                    moveShoe(draggedItem.index, index);
                    draggedItem.index = index;
                }
            }
        });

        const ref = (node) => {
            dragRef(node);
            dropRef(node);
        }

        return (
            <div
                key={shoe.urlKey}
                className="shoe-card"
                onClick={() => handleShoeClick(shoe)}
                ref={ref}
                style={isDragging ? { opacity: 0.5 } : {}}
            >
                <div className="image-container">
                    <img src={URL+"images/" + shoe.uuid + "/img/01.png"}onError={({ currentTarget }) => {
                                currentTarget.onerror = null; 
                                currentTarget.src= selectedShoe.imageUrl;
                                }}></img>
                </div>
                <div className="shoe-info">
                    <h4>{shoe.title}</h4>
                </div>
            </div>
        );
    };

    const moveShoe = (fromIndex, toIndex) => {
        const updatedPortfolio = [...portfolio];
        const [movedShoe] = updatedPortfolio.splice(fromIndex, 1);
        updatedPortfolio.splice(toIndex, 0, movedShoe);
        setPortfolio(updatedPortfolio);
    };

    const DroppablePortfolio = ({ children, onDrop }) => {
        const [, dropRef] = useDrop({
            accept: 'SHOE',
            drop: (item, monitor) => {
                const didDrop = monitor.didDrop();
                if (didDrop) {
                    return;
                }
                return onDrop(item, portfolio.length);
            }
        });

        return (
            <div ref={dropRef} className="shoe-grid">
                {React.Children.map(children, child => child)}
            </div>
        );
    };

    const handleDrop = (shoe, index) => {
        const updatedPortfolio = portfolio.filter(item => item.urlKey !== shoe.urlKey);

        updatedPortfolio.splice(index, 0, shoe);

        setPortfolio(updatedPortfolio);
    };

    return (
        <DndProvider backend={HTML5Backend}>
            <div className="App">
                <div className="App-header">
                    <h1>Sneaker portfolio</h1>
                    <div className="user-buttons">
                        {users.map(user => (
                            <button className="button"
                                key={user.id}
                                onClick={() => handleUserClick(user.id)}
                                style={selectedUserId === user.id.toString() ? { backgroundColor: 'black' } : {}}
                            >
                                {user.name}
                            </button>
                        ))}
                    </div>
                </div>
                <div style={{ marginTop: '20px' }}>
                    <button className="button" onClick={() => setIsSearchModalOpen(true)}>
                        Add Shoe
                    </button>
                </div>

                {isSearchModalOpen && (
                    <div className="search-modal-overlay">
                        <div className="search-modal-content">
                            <button className="button" onClick={() => setIsSearchModalOpen(false)}>
                                Close
                            </button>
                            <div style={{ marginTop: '20px' }}>

                                <input
                                    type="text"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    placeholder="Search for a shoe..."
                                    style={{
                                        width: '100%',
                                        padding: '12px',
                                        fontSize: '18px'
                                    }}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                            handleSearch();
                                        }
                                    }}
                                />
                            </div>
                            <div style={{ marginTop: '20px' }}>
                                <button className="button" onClick={handleSearch}>Search</button>
                            </div>

                            <div className="shoe-grid">
                                {searchResults.map(shoe => (
                                    <div key={shoe.urlKey} className="shoe-card" onClick={() => showSizeModal(shoe)}>
                                        <div className="image-container">
                                            <img src={shoe.thumbUrl} alt={shoe.title} />
                                        </div>
                                        <div className="shoe-info">
                                            <h4>{shoe.title}</h4>

                                        </div>
                                    </div>
                                ))}
                            </div>
                            <div style={{ marginTop: '20px' }}>
                                <button className="button" onClick={() => setIsSearchModalOpen(false)}>Close</button>
                            </div>
                        </div>
                    </div>
                )}

                {isSizeModalOpen && (
                    <div className="modal-overlay" onClick={() => setIsSizeModalOpen(false)}>
                        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                            <h3>Select Size for {selectedShoe.title}</h3>
                            <div style={{ marginTop: '20px' }}>
                                <div className="image-container">
                                    <img src={selectedShoe.imageUrl} alt={selectedShoe.title} />
                                </div>
                                <select onChange={(e) => setSelectedSize(e.target.value)}>

                                    <option value="40">40</option>
                                    <option value="40.5">40.5</option>
                                    <option value="41">41</option>
                                    <option value="42">42</option>
                                    <option value="42">42.5</option>
                                    <option value="43">43</option>
                                    <option value="44">44</option>
                                    <option value="44.5">44.5</option>
                                    <option value="45">45</option>
                                    <option value="45.5">45.5</option>
                                    <option value="46">46</option>
                                    <option value="47">47</option>
                                    <option value="47.5">47.5</option>
                                    <option value="48.5">48.5</option>
                                </select>
                            </div>
                            <div style={{ marginTop: '20px' }}>
                                <button className="button" onClick={addShoeToPortfolio}>
                                    Add to Portfolio
                                </button>
                            </div>
                            <div style={{ marginTop: '20px' }}>
                                <button className="button" onClick={() => setIsSizeModalOpen(false)}>
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                )}
                <div>
                    {selectedUserId && (
                        <>
                            <h3>Displaying portfolio {selectedUserId}</h3>
                            <DroppablePortfolio onDrop={handleDrop}>
                                {portfolio.map((shoe, idx) => (
                                    <DraggableShoeCard shoe={shoe} key={shoe.urlKey} index={idx} moveShoe={moveShoe} />
                                ))}
                            </DroppablePortfolio>
                        </>
                    )}
                </div>
                {isModalOpen && (
                    <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
                        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                            <h3 className="modal-title">{selectedShoe.title}</h3>
                            <div className="modal-gif">
                                <img src={URL + "images/" + selectedShoe.uuid+ "/gif/"+ selectedShoe.uuid +".gif"} alt={selectedShoe.title} 
                                onError={({ currentTarget }) => {
                                currentTarget.onerror = null; 
                                currentTarget.src= selectedShoe.imageUrl;
                                }} />
                            </div>
                            <div className="modal-text">
                                <h4>{selectedShoe.title}</h4>
                                <p><strong>Name:</strong> {selectedShoe.name}</p>
                                <p><strong>Colorway:</strong> {selectedShoe.model}</p>
                                <p><strong>Brand:</strong> {selectedShoe.brand}</p>
                                <p><strong>Release Date:</strong> {selectedShoe.release_date}</p>
                                <p><strong>Retail Price:</strong> {"$" + selectedShoe.retail_price}</p>
                                <p>
                                    <strong>Link:</strong>{" "}
                                    <a href={"https://stockx.com/" + selectedShoe.urlKey} target="_blank" rel="noopener noreferrer">
                                        {"https://stockx.com/" + selectedShoe.urlKey}
                                    </a>
                                </p>
                                <p><strong>Description:</strong> {selectedShoe.description}</p>
                            </div>
                            <div style={{ marginTop: '20px' }}>
                                <button className="button" onClick={handleShoeDelete}>Delete</button>
                            </div>
                            <div style={{ marginTop: '20px' }}>
                                <button className="button" onClick={() => setIsModalOpen(false)}>Close</button>
                            </div>
                        </div>
                    </div>
                )}



            </div>
        </DndProvider>
    );
}

export default MainScreen;
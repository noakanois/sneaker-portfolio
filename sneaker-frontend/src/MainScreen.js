import React, { useState, useEffect } from 'react';
import Heart from "react-animated-heart";
import axios from 'axios';
import './App.css';

import { HTML5Backend } from 'react-dnd-html5-backend';
import { DndProvider, useDrag, useDrop } from 'react-dnd';

const URL = process.env.REACT_APP_API_URL;

if (!URL) {
    alert("Please put a .env file in the react project folder with REACT_APP_API_URL defined like .env.template and restart the Server");
}

function MainScreen() {
    const [users, setUsers] = useState([]);
    const [portfolio, setPortfolio] = useState([]);
    const [selectedUserId, setSelectedUserId] = useState(localStorage.getItem('userId') || '1');
    const [selectedUser, setSelectedUser] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedShoe, setSelectedShoe] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
    const [isSizeModalOpen, setIsSizeModalOpen] = useState(false);
    const [greyOutNonFav, setGreyOutNonFav] = useState(false);

    axios.defaults.headers['ngrok-skip-browser-warning'] = 'true';

    const showSizeModal = (shoe) => {
        setSelectedShoe(shoe);
        setIsSizeModalOpen(true);
    }

    useEffect(() => {
        axios.get(URL + 'users').then(response => {
            const fetchedUsers = response.data;
            setUsers(fetchedUsers);
            let currentUserId = localStorage.getItem('userId') || fetchedUsers[0].id.toString();
            const currentUser = fetchedUsers.find(user => user.id.toString() === currentUserId);
            setSelectedUser(currentUser);
            setSelectedUserId(currentUser.id.toString());
        }).catch(error => {
            console.error("Error fetching users:", error);
        });
    }, []);

    useEffect(() => {
        if (selectedUserId) {
            handleUserClick(selectedUserId);
        }
    }, [selectedUserId]);

    const handleSearch = () => {
        axios.get(URL + 'search/name/' + searchTerm, { name: searchTerm }).then(response => {
            setSearchResults(response.data);
        });
    };
    const handleUserClick = async (userIdString) => {
        const userId = parseInt(userIdString, 10);
        const currentUser = users.find(user => user.id === userId);
        setSelectedUser(currentUser);
        setSelectedUserId(userId);
        localStorage.setItem('userId', userIdString);
        axios.defaults.headers['X-User-ID'] = userIdString;
        try {
            const response = await axios.get(URL + `user/${userId}/portfolio`);
            setPortfolio(response.data);
        } catch (error) {
            console.error("Failed to fetch portfolio for user:", error);
        }
    };

    const handleShoeClick = (shoe) => {
        setSelectedShoe(shoe);
        setIsModalOpen(true);
    }
    const addShoeToPortfolio = () => {
        axios.post(URL + 'user/addToPortfolio', {
            userId: selectedUserId,
            shoeTitle: selectedShoe.title,
        })
            .then(response => {
                if (response.status !== 200) {
                    alert('Failed to add item to portfolio. Please try again.');
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
        axios.delete(URL + `user/${selectedUserId}/portfolio/${selectedShoe.uuid}`)
            .then(response => {
                setIsModalOpen(false);
                handleUserClick(selectedUserId);
            })
            .catch(error => {
                alert("Error removing shoe from portfolio");
                console.error("Error:", error);
            });
    }



    const DraggableShoeCard = ({shoe, index, moveShoe, greyOutNonFav }) => {
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
        const getPortfolioIndex = ({ uuid }) => {
            return portfolio.findIndex(item => item.uuid === uuid);
        }
        const getFavoriteStatus = ({ uuid }) => {
            const index = getPortfolioIndex({ uuid });
            return portfolio[index]["favorite"];
        }
        const toggleFavoriteStatus = ({ uuid }) => {
            const status = !getFavoriteStatus({ uuid })
            axios.post(URL + `favorites/${selectedUserId}/set/${uuid}/${status}`);
            const updatedPortfolio = [...portfolio];
            const index = getPortfolioIndex({ uuid });
            updatedPortfolio[index] = {
                ...updatedPortfolio[index],
                favorite: !updatedPortfolio[index].favorite
            };
            setPortfolio(updatedPortfolio);
        };
        return (
            <div
                key={shoe.uuid}
                className={`shoe-card ${greyOutNonFav && !shoe.favorite ? 'greyed-out' : ''}`}
                onClick={() => handleShoeClick(shoe)}
                ref={ref}
                style={isDragging ? { opacity: 0.5 } : {}}
            >
                <div className="image-container">
                    <img src={URL + "images/" + shoe.uuid + "/img/" + shoe.uuid + ".png"} onError={({ currentTarget }) => {
                        currentTarget.onerror = null;
                        currentTarget.src = shoe.imageUrl;
                    }}></img>
                    <img className="gif" src={URL + "images/" + shoe.uuid + "/gif/" + shoe.uuid + ".gif"} onError={({ currentTarget }) => {
                        currentTarget.onerror = null;
                        currentTarget.src = shoe.imageUrl;
                    }}></img>
                </div>
                <div className="favourite-heart">
                    <Heart isClick={portfolio[getPortfolioIndex({ uuid: shoe.uuid })]["favorite"]} onClick={(event) => { toggleFavoriteStatus({ uuid: shoe.uuid }); event.stopPropagation() }} />
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
        const updatedOrder = updatedPortfolio.map(shoe => shoe.uuid);
        axios.post(URL + `user/${selectedUserId}/portfolio/reorder`, { shoe_uuids: updatedOrder });
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
            <div className="main-grid">
                <div ref={dropRef} className="shoe-grid">
                    {React.Children.map(children, child => child)}
                </div>
            </div>
        );
    };
    const handleDrop = (shoe, index) => {
        const updatedPortfolio = portfolio.filter(item => item.uuid !== shoe.uuid);
        updatedPortfolio.splice(index, 0, shoe);
        setPortfolio(updatedPortfolio);
    };


    const getRandomShoe = () => {
        let shoes = greyOutNonFav ? portfolio.filter(shoe => shoe.favorite) : portfolio;
        if (shoes.length === 0) {
            alert('No items in the portfolio to select from!');
            return;
        }
        const randomIndex = Math.floor(Math.random() * shoes.length);
        const randomShoe = shoes[randomIndex];
        setSelectedShoe(randomShoe);
        setIsModalOpen(true);
    }

    const Navbar = ({ users, handleUserClick, selectedUserId, selectedUser }) => (
        <div className="navbar">
            <div className="navbar-brand">
                Sneaker Portfolio
            </div>
            <div className="user-dropdown">
                <span style={{ fontSize: '24px', cursor: 'pointer' }}>
                    {selectedUser ? selectedUser.name : 'Loading...'}
                </span>
                <div className="user-dropdown-content">
                    {users.map(user => (
                        <a
                            key={user.id}
                            onClick={() => handleUserClick(user.id)}
                            style={selectedUserId === user.id.toString() ? { backgroundColor: '#ddd' } : {}}
                        >
                            {user.name}
                        </a>
                    ))}
                </div>
            </div>

            <div className="action-buttons">
                <button className="action-button add" onClick={() => setIsSearchModalOpen(true)}>+</button>
                <button className="action-button random" onClick={getRandomShoe}>🎲 </button>
                <button className="action-button favorite" onClick={() => setGreyOutNonFav(!greyOutNonFav)}>❤️</button>
            </div>
        </div>
    );

    return (
        <DndProvider backend={HTML5Backend}>
            <div className="App">
                <Navbar
                    users={users}
                    handleUserClick={handleUserClick}
                    selectedUser={selectedUser}
                />
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
                                    placeholder="Search for an item..."
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
                                    <div key={shoe.uuid} className="shoe-card" onClick={() => showSizeModal(shoe)}>
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
                            <button className="button" onClick={() => setIsSizeModalOpen(false)}>
                                Close
                            </button>
                            <h3>Select Size for {selectedShoe.title}</h3>
                            <div style={{ marginTop: '20px' }}>
                                <div className="image-container">
                                    <img src={selectedShoe.imageUrl} alt={selectedShoe.title} />
                                </div>
                            </div>
                            <div style={{ marginTop: '20px' }}>
                                <button className="button" onClick={addShoeToPortfolio}>
                                    Add to Portfolio
                                </button>
                            </div>
                            <div style={{ marginTop: '20px' }}>
                                <button className="button" onClick={() => setIsSizeModalOpen(false)}>
                                    Close
                                </button>
                            </div>
                        </div>
                    </div>
                )}
                <div>
                    {selectedUserId && (
                        <>

                            <DroppablePortfolio onDrop={handleDrop}>
                                {portfolio.map((shoe, idx) => (
                                    <DraggableShoeCard shoe={shoe} key={shoe.uuid} index={idx} moveShoe={moveShoe} greyOutNonFav={greyOutNonFav} />
                                ))}
                            </DroppablePortfolio>
                        </>
                    )}
                </div>
                {isModalOpen && (
                    <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
                        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                            <button className="button" onClick={() => setIsModalOpen(false)}>Close</button>
                            <h3 className="modal-title">{selectedShoe.title}</h3>
                            <div className="modal-gif">
                                <img src={URL + "images/" + selectedShoe.uuid + "/gif/" + selectedShoe.uuid + ".gif"} alt={selectedShoe.title}
                                    onError={({ currentTarget }) => {
                                        currentTarget.onerror = null;
                                        currentTarget.src = selectedShoe.imageUrl;
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
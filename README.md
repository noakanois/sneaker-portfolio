
<p align="center">
<img src = readme-media/gifs/portfolio.gif > </img>
</p>
<h1 align="center"> Sneaker Portfolio   </h1>

<font size=5px>
<b align="center">

<a href="https://nsli.me"> 👟 Check out the Website 👟</a>

</b>
</font >

Sneaker Portfolio is an interactive Website which allows you to track your shoe collection in a visual portfolio. You can search, add, and remove shoes in order to keep it up to date. The portfolio can be presented in any order and includes features such as a random picker 🎲. Not only can you show off your collection easier to your friends, but you can also make yourself a better picture on what shoes you could buy next. 


## Table of Contents


- [Feature Showcase](#feature-showcase)
- [How to use?](#how-to-use)
  - [Docker 🐳](#docker-)
  - [Requirements](#requirements)
  - [Step by Step Tutorial](#step-by-step-tutorial)
  - [Commands](#commands)
    - [Backend](#backend)
    - [Frontend](#frontend)
- [Future features](#future-features)


## Feature Showcase




*[CLICK TO EXPAND]*
<details>
    <summary> 360 Degree Animations</summary>
    <br> 
    <img src = readme-media/gifs/360.gif > </img>
</details>

<details>
    <summary>Drag & Drop </summary>
    <br> 
    <img src = readme-media/gifs/draganddrop.gif > </img>
</details>

<details>
    <summary>Get Shoe Information & Links</summary>
    <br> 
    <img src = readme-media/gifs/information.gif > </img>
</details>

<details>
    <summary>Add Shoes</summary>
    <br> 
    <img src = readme-media/gifs/add.gif > </img>
</details>


<details>
    <summary>Remove Shoes</summary>
    <br> 
    <img src = readme-media/gifs/remove.gif > </img>
</details>

<details>
    <summary>Get Random Shoe 🎲</summary>
    <br> 
    <img src = readme-media/gifs/random.gif > </img>
</details>

<details>
    <summary>Favorite View ❤️</summary>
    <br> 
    <img src = readme-media/gifs/favorite.gif > </img>
</details>






## How to use?

**BEFORE YOU START THE APPLICATION:**


- The variable `REACT_APP_API_URL` has to be configured to the URL the application will be running on. If you run it on your local machine, it has to be configured to `http://localhost:8000/`.
- To configure the variable, add a `.env` file in `sneaker-frontend` similar to the `.env.template` found in the same folder 
- 
### Docker 🐳

We heavily encourage running the application through Docker. Run `docker-compose up` to start it on default port `8000`.



### Requirements
If you want to run the application locally, installing `Python 3.11`, `poetry`, `nodejs` and `npm` is necessary.

Using [conda](https://docs.conda.io/en/latest/) is recommended for the Python setup.



### Step by Step Tutorial

<details>
    <summary>Commands with conda
    </summary>
    If you are using conda, run: 

<ol>
    

<li> <code>conda create -n sneaker python=3.11 </code></li>
<li> <code>conda activate sneaker </code></li>
<li> <code>pip install poetry </code></li>

</ol>

</details>



To run the application, run these commands:
1. `make install-server` 
2. `make build`
3. `make server`



### Commands
#### Backend

- `make install-server` to install dependencies.
- `make server` to start the Python FastAPI backend server on default port `8000`.


#### Frontend

- `make build` to install dependencies and generate static webpages with React. These webpages can then be served by the backend. 
- `make frontend` starts a webserver serving the websites on default port `3000`.



## Further documentation

- [API endpoints](api-endpoints.md)
## Future features

- Creation of new users via the Frotnend. Currently, there is a fix amount of users added by hand to the database.
- Insertion of custom entries, in case StockX does not have a shoe available.
- ...
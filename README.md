# Sneaker Portfolio  👟 



# [Website](https://nsli.me) <-- Check it out

<img src = readme-media/gifs/portfolio.gif > </img>
## Table of Contents

- [Feature Showcase](#feature-showcase)
- [How to use?](#how-to-use)
  - [Backend](#backend)
  - [Frontend](#frontend)
  - [Docker 🐳](#docker-)
- [API Endpoints](#api-endpoints)
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

The application consists of a back- and frontend. For it to work, both of the services have to be running.

**BEFORE YOU START THE APPLICATION:**


- The variable `REACT_APP_API_URL` has to be configured to the URL the application will be running on. If you run it on your local machine, it has to be configured to `http://localhost:8000/`.
- To configure the variable, add a `.env` file in `sneaker-frontend` similar to the `.env.template` found in the same folder 


### Backend

- `make install-server` to install dependencies
- `make server` to start the server on port `8000`


### Frontend

- `make build` to install dependencies and generate static webpages. The frontend will also be accessible through port `8000
- `make frontend` for development of the website on port `3000`.


### Docker 🐳

- The application can also be run through docker. Simply run `docker-compose up` to start both front- and backend.


## API Endpoints

- `/users`
  
       `GET`: Get a list of all users in the database.
- `/user` 
  - `/addToPortfolio`
    
        `POST; {userId: str, shoeTitle:str}`: Add a shoe with the title `shoeTitle` to the user with the id `userId`
  
   - `/{user_id}/portfolio`,
    
         `GET`: Get the portfolio onformation af the user with `user_id`
  - `/{user_id}/portfolio/{shoe_uuid}`
 
        DELETE {user_id: int, shoe_uuid: str}: Remove the shoe with uuid `shoe_uuid` from the user `user_id`

  - `/{user_id}/portfolio/reorder`
        
        POST {user_id: int, order_data: List[str] }: Reorder the portfolio of user with id `user_id` according to the `order_data`
- `/search/name/{name}`
        
      `GET`: Get a list of the search results with the search term `name`
- `/favorites/{user_id}/set/{shoe_uuid}/{status}`
     
      POST {user_id: int, shoe_uuid: str, status: bool}: Change the favorite status to `status` of the shoe with uuid `shoe_uuid` in the user with the id `user_id`

## Future features

- Allow addition of users
- ...
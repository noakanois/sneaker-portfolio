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

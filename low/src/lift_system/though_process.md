## Let first understand what all flow are going to be there

Initially, lift will be at 0th floor. Someone will call the lift from 0th floor to some valid floor `n`. Lift will start moving in that direction. If someone calls lift inbetween, then it will first stop on that floor.

Once reached, door should open. After some defined time, door should close. if someone press, open door/close door while lift is on that floor, then doors should open/close.

Once, door are closed/open, lift should be able to take user input for the floor numbers and it should count the number of persons are well so that it does not carry excessive load.

Once, lift receives input of destination floor or floors then it should start moving in that direction. If someone calls lift inbetween, then it will first stop on that floor. Here, make sure of the direction that the lift was moving to.


And the cycle continues.


## What all entities are going to be there in this design?
### User related
None as such

### lift related
#### common entities
    1. Button
    2. Display
    3. Direction
#### Outside of lift
    1. Outside panel [for each floor]
        allowed operations: 
            - call lift to that floor
    2. outside display [for each floor]
        allowed operations:
            - show current floor number of the lift
            - show moving direction of the lift
#### Inside of lift
    1. Inside panel [one for each lift]
        allowed operations:
            - open door
            - close door
            - select floor number
    2. Inside display [one for each lift]
            - show current floor number
            - show number of persons in lift

### connecting entities
1. Floor
   Contains:
    - Floor number
    - Outside panel
    - Outside display
2. Lift:
   Contains:
   - Inside panel
   - Inside display
   - Direction


## What all potential design patterns will be used?
1. Observer pattern
   - Outside display will be observer of lift
   - Inside display will be observer of lift
   - Once a floor is reached, message has to be beeped
2. State design pattern
   - Lift will be in different states like moving, stopped, door open, door closed, etc.
   - Based on the state, different operations will be allowed.
3. Command design pattern
   - Lift will have different commands like open door, close door, select floor, etc.
   - Each command will be executed based on the current state of the lift.
4. Strategy design pattern
   - Lift will have different strategies for moving in different directions.
   - Based on the direction, lift will move accordingly.
   - There has to be a strategy to choose, if there are multiple lifts

## will there be a need for threading and concurrency control?
1. Need for threading: Yes, at the background, lift must be moving with a constant speed.
2. Concurrency control: Yes, there can be multiple inputs at the same time like someone can call lift from outside and someone can select floor from inside. So, there should be a way to handle these inputs in a thread-safe manner.
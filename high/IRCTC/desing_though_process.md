Let first understand what all components we need to design

1. User
   1. Normal User
   2. Admin User
2. Train
   1. Various type of Coaches
      1. Sleeper
      2. AC
      3. General
   2. No of seats in each coach or coach type



Flow that we need to handle - 

1. User Onboarding and handling
2. Train schedules Flow
   1. Same train on different dates
   2. 
3. Train Booking Flow
4. History of Booking
5. Analytics
6. Optimizations based on 
   1. User search
   2. Stations based on high traffic


Let split user into two types -
1. Normal User
2. Admin User
   1. Admin User has the privilege to update the train schedule
        1. What sort of database should we use to store the train schedule?

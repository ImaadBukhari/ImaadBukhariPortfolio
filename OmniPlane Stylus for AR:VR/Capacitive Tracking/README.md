## This is a testament to a failure

Our initial solution to the problem was a solution that had both high accuracy and high precision. What we came up with was quite a complicated hardware approach that used capacitance just like a traditional touch screen, but reimagined. 

Essentially, the problem boiled down to recognizing patterns with limited sensors and no objective reference of where the pen is. 
![pattern2](https://github.com/user-attachments/assets/a7e40f98-e542-4706-8ba0-adcde209a948)

For example, when going over this pattern, we wanted to be able to predict the pattern underneath with a system of sensors arranged as follows:

![grid_image_gridded](https://github.com/user-attachments/assets/a8475ece-9ad8-40ff-a8b8-880e852acaf4)

Unfortunately, we were not able to accomplish this. Without having a reference, the pattern of sensors could be at any orientation in any position. There was no robust way we could find to predict the pattern underneath with high accuracy. 

Our best attempt is in Rotation Algorithm OOP. It uses a Monte Carlo style approach that embraces error to predict multiple possibilities multiple times, and trying to find commonality there. It was actually very effective, but too slow to be used in real time for a stylus pen.  

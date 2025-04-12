# Computer Vision Based Tracking

To track a stylus pen in 3D space, we largely made use of open source computer vision models. 

### HSV Masking

We used a color based mask to isolate an anchor point on the stylus pen and used this to track it throughout video frames with a Lucas_kanade based approach. 

![purple_detection_comparison](https://github.com/user-attachments/assets/e3e3bbf7-feb6-4fb7-adcb-21b096b53bb7)


###  Stereo Optics

We added stereo optics to this to be able to account for depth and track the stylus pen in 3D space. 

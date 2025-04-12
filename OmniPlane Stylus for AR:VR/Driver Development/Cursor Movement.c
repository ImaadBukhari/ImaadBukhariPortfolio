#include <ApplicationServices/ApplicationServices.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Function to move the cursor to a specific point
void move_cursor(float x, float y) {
    CGEventRef move = CGEventCreateMouseEvent(NULL, kCGEventMouseMoved, CGPointMake(x, y), kCGMouseButtonLeft);
    CGEventPost(kCGHIDEventTap, move);
    CFRelease(move);
}

// Function to perform a click at a specific point
void click_cursor(float x, float y) {
    // Move to the location 
    move_cursor(x, y);
    // Mouse down
    CGEventRef click_down = CGEventCreateMouseEvent(NULL, kCGEventLeftMouseDown, CGPointMake(x, y), kCGMouseButtonLeft);
    CGEventPost(kCGHIDEventTap, click_down);
    CFRelease(click_down);

    //Mouse up
    CGEventRef click_up = CGEventCreateMouseEvent(NULL,kCGEventLeftMouseUp, CGPointMake(x, y), kCGMouseButtonLeft);
    CGEventPost(kCGHIDEventTap, click_up);
    CFRelease(click_up);
}




// Function to perform click and drag as the cursor moves from one location to another
void click_drag(float start_x, float start_y, float end_x, float end_y) {
    // First move to the starting location
    move_cursor(start_x, start_y);
    // Mouse down
    CGEventRef drag_start = CGEventCreateMouseEvent(NULL, kCGEventLeftMouseDown, CGPointMake(start_x, start_y), kCGMouseButtonLeft);
    CGEventPost(kCGHIDEventTap, drag_start);
    CFRelease(drag_start);

    // Purpose: The for loop helps to run 'steps' times to create intermediate points between the start and end positions. This
    // can smooth the movement to make it appear more like a natural drag.
    int steps = 100;
    
    for (int i = 0; i < steps; i++) {
        float x = start_x + (end_x - start_x) * ((float)i / steps);
        float y = start_y + (end_y - start_y) * ((float)i / steps);
        CGEventRef drag = CGEventCreateMouseEvent(NULL, kCGEventLeftMouseDragged, CGPointMake(end_x, end_y), kCGMouseButtonLeft);
        CGEventPost(kCGHIDEventTap, drag);
        CFRelease(drag);
        // 'usleep' pauses the loopfor a short duration, this delay helps in making the movement appear smooth
        usleep(10000); 
    }

    // Mouse up
    CGEventRef drag_end = CGEventCreateMouseEvent(NULL, kCGEventLeftMouseUp, CGPointMake(end_x, end_y), kCGMouseButtonLeft);
    CGEventPost(kCGHIDEventTap, drag_end);
    CFRelease(drag_end);

}

// function to make the cursor move without clicking to different points
// parameters: points[] are the points through which the cursor should move.
// num_points is the total number of points that the cursor should go through
// duration is the total duration (in seconds) over which the cursor should move through all points, it can determine how long 
// the cursor should take to move from one point to the next and ensures smooth movement
void move_cursor_no_click(CGPoint points[], int num_points) {
    // Calculate number of steps for smooth movement
    int steps = 100;
    

    for (int i = 0; i < num_points - 1; i++) {
        float start_x = points[i].x;
        float start_y = points[i].y;
        float end_x = points[i + 1].x;
        float end_y = points[i + 1].y;

        for (int j = 0; j < steps; j++) {
            float x = start_x + (end_x - start_x) * ((float)j / steps);
            float y = start_y + (end_y - start_y) * ((float)j / steps);
            move_cursor(x, y);
            usleep(10000); // Sleep to make the movement smooth
        }
    }

    // Move cursor to the last point
    move_cursor(points[num_points - 1].x, points[num_points - 1].y);
}
int main() {
    
    //CGPoint points[] = {{100, 100}, {200, 200}, {300, 300}, {400, 400}, {500, 500}};
    //int num_points = sizeof(points) / sizeof(points[0]);
    //float duration = 2.0;
    
    //move_cursor_no_click(points, num_points);

    //click_cursor(500, 500);

    
    // receiving inputs from pyton program
    float x, y;
    bool pressed, last_pressed = false;
    float last_x, last_y;
    CGPoint points[2]; // To store points for smooth movement or drag
    int point_index = 0;

    while (scanf("%f %f %d", &x, &y, &pressed) == 3) {
        if (pressed) {
            if (last_pressed) {
                // Dragging
                points[point_index].x = last_x;
                points[point_index].y = last_y;
                point_index++;
                points[point_index].x = x;
                points[point_index].y = y;
                move_cursor_no_click(points, point_index + 1);
                click_drag(last_x, last_y, x, y);
                point_index = 0; // Reset point index after drag
            } else {
                // Clicking
                click_cursor(x, y);
            }
        } else {
            // Move without clicking
            move_cursor(x, y);
        }
        last_x = x;
        last_y = y;
        last_pressed = pressed;
        usleep(100000); // Adjust sleep time to match the data rate from the Python program
    }


    
    
    return 0;
}
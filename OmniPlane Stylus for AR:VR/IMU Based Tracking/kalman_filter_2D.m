clear;
clc;
close all;

% Serial Port Setup
serialPort = "/dev/tty.usbserial-210"; % Change to match your Arduino port
baudRate = 115200;
s = serialport(serialPort, baudRate, "Timeout", 2);

% AHRS Initialization
samplePeriod = 1/200;
AHRSalgorithm = AHRS('SamplePeriod', samplePeriod, 'Kp', 1, 'KpInit', 1);

% EKF Initialization (State: Position, Velocity, Orientation)
x = zeros(9,1); % [px, py, pz, vx, vy, vz, q1, q2, q3, q4]
P = eye(9) * 0.1; % Initial covariance matrix
Q = eye(9) * 0.01; % Process noise covariance
R = eye(6) * 0.05; % Measurement noise covariance

numSamples = 1000;
quatData = zeros(numSamples, 4);
posData = zeros(numSamples, 3);
rawAccelData = zeros(numSamples, 3);
rawGyroData = zeros(numSamples, 3);

previousValidAccel = [0, 0, 0];

%% Gravity Calibration (Estimate Gravity Vector at Rest)
restSamples = 400;
restAccelData = zeros(restSamples, 3);

disp("Place the device at rest for 2 seconds to estimate gravity...");
restIndex = 1;
startTime = tic;
while toc(startTime) < 2  
    if s.NumBytesAvailable > 9  
        prefix = read(s, 1, "uint8");  
        if prefix == uint8('A')  
            timestamp = read(s, 1, "uint32");  
            accelData = read(s, 3, "single");  

            if any(abs(accelData) > 1e6) || any(abs(accelData) < 50)
                continue; 
            end
            
            restAccelData(restIndex, :) = accelData;
            restIndex = restIndex + 1;
            if restIndex > restSamples
                break;
            end
        end
    end
end

validRestData = restAccelData(any(restAccelData ~= 0, 2), :);
gGravity = mean(validRestData, 1);

disp("Estimated Gravity Vector:");
disp(gGravity);

%% Data Collection with EKF Filtering
startTime = tic;
sampleIndex = 1;
alpha = 0.05; % More aggressive low-pass filter weight

disp("Collecting Data for 5 seconds with EKF...");
while toc(startTime) < 1  
    if s.NumBytesAvailable > 9  
        prefix = read(s, 1, "uint8");  
        if prefix == uint8('A')  
            timestamp = read(s, 1, "uint32");  
            accelData = read(s, 3, "single");  
            gyroData = read(s, 3, "single");  

            if any(abs(accelData) > 1e6) || any(abs(accelData) < 50)
                accelData = previousValidAccel;
            else
                accelData = alpha * accelData + (1 - alpha) * previousValidAccel; % Apply low-pass filter
                previousValidAccel = accelData;
            end
            
            if any(abs(gyroData) > 1e6)
                continue;
            end
            
            % Gravity Compensation
            accelDataCorrected = accelData - gGravity;
            accelMag = sqrt(sum(accelDataCorrected.^2));
            
            % High-Pass Filter: Zero-out values below noise threshold
            staticThreshold = 0.02;
            if accelMag < staticThreshold
                accelDataCorrected = [0, 0, 0];
            end
            
            % EKF Prediction Step
            dt = samplePeriod;
            F = eye(9); % State transition model
            F(1:3,4:6) = eye(3) * dt; % Position update from velocity
            
            % Simple process model with acceleration integration
            x(1:3) = x(1:3) + x(4:6) * dt + 0.5 * accelDataCorrected(:) * dt^2;
            x(4:6) = x(4:6) + accelDataCorrected(:) * dt;
            P = F * P * F' + Q; % Covariance update
            
            % EKF Update Step (Fusion of Acceleration & Gyro Data)
            H = eye(6, 9); % Measurement matrix
            z = [accelDataCorrected, gyroData]'; % Measurement vector
            y = z - H * x; % Innovation (Residual)
            S = H * P * H' + R; % Innovation Covariance
            K = P * H' / S; % Kalman Gain
            x = x + K * y; % State Update
            P = (eye(9) - K * H) * P; % Covariance Update
            
            % Store Data
            quatData(sampleIndex, :) = AHRSalgorithm.Quaternion;
            posData(sampleIndex, :) = x(1:3);
            rawAccelData(sampleIndex, :) = accelDataCorrected;
            rawGyroData(sampleIndex, :) = gyroData;
            
            sampleIndex = sampleIndex + 1;
            if sampleIndex > numSamples
                break;
            end
        end
    end
end

%% Visualization
figure;
subplot(3,1,1);
plot(rawAccelData);
title("Filtered Acceleration Data");
legend('X', 'Y', 'Z');

subplot(3,1,2);
plot(rawGyroData);
title("Filtered Gyroscope Data");
legend('X', 'Y', 'Z');

subplot(3,1,3);
plot(posData);
title("Smoothed Position Data");
legend('X', 'Y', 'Z');

% 3D Motion Visualization
numSamples = size(quatData, 1);
rotMatData = zeros(3, 3, numSamples);
for i = 1:numSamples
    rotMatData(:, :, i) = quatern2rotMat(quatData(i, :));
end

%% 2D Projection of Position Data
figure;

% Choose a projection plane (XY, XZ, or YZ)
projectionPlane = 'XY'; % Change to 'XZ' or 'YZ' if needed

switch projectionPlane
    case 'XY'
        xData = posData(:,1);
        yData = posData(:,2);
        xlabel('X Position');
        ylabel('Y Position');
    case 'XZ'
        xData = posData(:,1);
        yData = posData(:,3);
        xlabel('X Position');
        ylabel('Z Position');
    case 'YZ'
        xData = posData(:,2);
        yData = posData(:,3);
        xlabel('Y Position');
        ylabel('Z Position');
end

plot(xData, yData, 'b-', 'LineWidth', 2);
hold on;
scatter(xData(1), yData(1), 50, 'g', 'filled'); % Start point
scatter(xData(end), yData(end), 50, 'r', 'filled'); % End point
grid on;
title(['2D Projection on ', projectionPlane, ' Plane']);
axis equal;

disp(['Displaying 2D projection on ', projectionPlane, ' plane']);


disp("Visualization complete.");


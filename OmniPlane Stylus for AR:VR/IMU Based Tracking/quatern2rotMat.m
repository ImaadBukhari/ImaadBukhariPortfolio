function R = quatern2rotMat(q)
    % Convert quaternion to rotation matrix
    R = [...
        1 - 2*(q(3)^2 + q(4)^2),  2*(q(2)*q(3) - q(1)*q(4)),  2*(q(2)*q(4) + q(1)*q(3));
        2*(q(2)*q(3) + q(1)*q(4)),  1 - 2*(q(2)^2 + q(4)^2),  2*(q(3)*q(4) - q(1)*q(2));
        2*(q(2)*q(4) - q(1)*q(3)),  2*(q(3)*q(4) + q(1)*q(2)),  1 - 2*(q(2)^2 + q(3)^2) ];
end

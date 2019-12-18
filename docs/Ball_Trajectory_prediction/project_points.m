function [xp] = project_points(X,f,c,k,alpha)

%Projects a 3D structure onto the image plane.
%
%INPUT: X: 3D structure in the world coordinate frame (3xN matrix for N points)
%       f: camera focal length in units of horizontal and vertical pixel units (2x1 vector)
%       c: principal point location in pixel units (2x1 vector)
%       k: Distortion coefficients (radial and tangential) (4x1 vector)
%       alpha: Skew coefficient between x and y pixel (alpha = 0 <=> square pixels)
%
%OUTPUT: xp: Projected pixel coordinates (2xN matrix for N points)
%Definitions:
%Let P be a point in 3D of coordinates X in the world reference frame (stored in the matrix X)
%The coordinate vector of P in the camera reference frame is: Xc = R*X + T
%where R is the rotation matrix corresponding to the rotation vector om: R = rodrigues(om);
%call x, y and z the 3 coordinates of Xc: x = Xc(1); y = Xc(2); z = Xc(3);
%The pinehole projection coordinates of P is [a;b] where a=x/z and b=y/z.
%call r^2 = a^2 + b^2.
%The distorted point coordinates are: xd = [xx;yy] where:
%
%xx = a * (1 + kc(1)*r^2 + kc(2)*r^4 + kc(5)*r^6)      +      2*kc(3)*a*b + kc(4)*(r^2 + 2*a^2);
%yy = b * (1 + kc(1)*r^2 + kc(2)*r^4 + kc(5)*r^6)      +      kc(3)*(r^2 + 2*b^2) + 2*kc(4)*a*b;
%
%The left terms correspond to radial distortion (6th degree), the right terms correspond to tangential distortion
%
%Finally, convertion into pixel coordinates: The final pixel coordinates vector xp=[xxp;yyp] where:
%
%xxp = f(1)*(xx + alpha*yy) + c(1)
%yyp = f(2)*yy + c(2)

for i=1:length(X(1,:))
B=X(:,i)/X(3,i);

kk=zeros(3,3);

kk(1,1)=f(1);
kk(1,2)=alpha*f(1);
kk(1,3)=c(1);
kk(2,2)=f(2);
kk(2,3)=c(2);
kk(3,3)=1;

r=(B(1)^2+B(2)^2)^0.5;
x_d(1)=(1+k(1)*r^2+k(2)*r^4+k(5)*r^6)*B(1)+2*k(3)*B(1)*B(2)+k(4)*(r^2+2*B(1)^2);
x_d(2)=(1+k(1)*r^2+k(2)*r^4+k(5)*r^6)*B(2)+k(3)*(r^2+2*B(2)^2)+2*k(4)*B(1)*B(2);
x_d(3)=1;
xd=[x_d(1) x_d(2) x_d(3)];
xpp=kk*xd';
xp(:,i)=xpp(1:2)';

end

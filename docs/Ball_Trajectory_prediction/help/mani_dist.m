function [d]=mani_dist(a,b)
%[m n]=size(a);
%[m1 n1]=size(b);
for i=1:length(a)
    if i==length(a)
        break;
    else
    x=abs(a(i)-a(i+1));
    y=abs(b(i)-b(i+1));
    x=x.^2;
    y=y.^2;
    d(i,1)=sqrt(x+y);
    end
end
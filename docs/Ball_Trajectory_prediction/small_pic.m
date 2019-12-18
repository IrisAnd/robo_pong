function bounds = small_pic (center , box)


% take bounds of picture 640x480 and limit it to box

if isempty(center)
    bounds=[1 640 ; 1 480];
    return;
end
if (center(1) - box ) > 1 
    bounds (1,1) = round(center(1) - box);
else
    bounds (1,1) = 1;
end
    
if (center(1) + box ) < 640 
    bounds (1,2) = round(center(1) + box);
else
    bounds (1,2) = 640;
end

if (center(2) - box ) > 1 
    bounds (2,1) = round(center(2) - box);
else
    bounds (2,1) = 1;
end

if (center(2) + box ) < 480
    bounds (2,2) = round(center(2) + box);
else
    bounds (2,2) = 480;
end

end
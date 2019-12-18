%%
% preview red ball in two cameras with subplot

close all

if exist ('vid1' , 'var')
    stop(vid1);
end

if exist ('vid2' , 'var')
    stop(vid2);
end
%%
vid1 = init_vid(1);
vid2 = init_vid(2);

%%
start(vid1);
start(vid2);

%%
trigger([vid1 , vid2]);

left_pic = getdata(vid1);
right_pic = getdata(vid2);

figure(1);

subplot(1, 2, 1)
h1=imshow(left_pic);
line1=line(rand(1,100),rand(1,100));
rect1=rectangle('Position',[1 2 3 4],'EdgeColor','r','LineWidth',2);


subplot(1, 2, 2)
h2=imshow(right_pic);
line2=line(rand(1,100),rand(1,100));
rect2=rectangle('Position',[1 2 3 4],'EdgeColor','r','LineWidth',2);

box=50;
Center1=[];
Bounding1=[];
Center2=[];
Bounding2=[];

tic;
for i=1:200

    trigger([vid1 , vid2]);
    left_pic = getdata(vid1);
    right_pic = getdata(vid2); 
        
    %left_pic(:,:,1)=0;
    %right_pic(:,:,2:3)=0;
    
    % Display the images
    
    set(h1,'cdata',left_pic);
    set(h2,'cdata',right_pic);
     
    [Center1 , Bounding1] = fast_find_ball(left_pic , Center1 , box);  
    [Center2 , Bounding2] = fast_find_ball(right_pic , Center2 , box);
       
    if isempty(Center1) || isempty(Center2)
        continue;
    end
    
    set(rect1,'Position',Bounding1,'EdgeColor','r','LineWidth',2);
  
    set(line1,'xdata',Center1(1),'ydata',Center1(2) ,...
                'LineStyle' ,'-' ,'Marker' ,'+','Color', [1 0 1]);
            
    set(rect2,'Position',Bounding2,'EdgeColor','r','LineWidth',2);
  
    set(line2,'xdata',Center2(1),'ydata',Center2(2) ,...
                'LineStyle' ,'-' ,'Marker' ,'+','Color', [1 0 1]);

end

i/toc

% Stop the video aquisition.
stop(vid1);
stop(vid2);

% Flush all the image data stored in the memory buffer.
flushdata(vid1);
flushdata(vid2);
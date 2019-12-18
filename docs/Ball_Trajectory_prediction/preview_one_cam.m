%%

% preview red ball in one camera

close all

if exist ('vid1' , 'var')
    stop(vid1);
end

if exist ('vid2' , 'var')
    stop(vid2);
end
%%

vid1 = init_vid(1);

%%
start(vid1);

%%

trigger(vid1);
left_pic = getdata(vid1);

figure(1);
h1=imshow(left_pic);
line1=line(rand(1,100),rand(1,100));
rect1=rectangle('Position',[1 2 3 4],'EdgeColor','r','LineWidth',2);

box=50;
Center1=[];
tic;
for i=1:200

    trigger(vid1);
    left_pic = getdata(vid1);
    
    % Display the image
  
    set(h1,'cdata',left_pic);
    
    [Center1 , Bounding1] = fast_find_ball(left_pic , Center1 , box); 
    
    if isempty(Center1)
        continue;
    end
 
    set(rect1,'Position',Bounding1,'EdgeColor','r','LineWidth',2)
 
    set(line1,'xdata',Center1(1),'ydata',Center1(2) ,...
                'LineStyle' ,'-' ,'Marker' ,'+','Color', [1 0 1]);
       

end

i/toc

% Stop the video aquisition.
stop(vid1);

% Flush all the image data stored in the memory buffer.
flushdata(vid1);
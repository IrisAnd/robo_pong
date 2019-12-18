%% close cameras if open
close all

if exist  ('vid1' , 'var')
    stop(vid1);
end

if exist ('vid2' , 'var')
    stop(vid2);
end

%% initial cameras
vid1=init_vid(1);
vid2=init_vid(2);

%% start the cameras
start(vid1);
start(vid2);

trigger([vid1 , vid2]);

% Get the snapshot of the current frame
left_pic = getdata(vid1);
right_pic = getdata(vid2);


figure(1);
% subplot(1, 2, 1)
h1=imshow(left_pic);

line1=line(4*rand(1,100),4*rand(1,100));
rect1=rectangle('Position',[1 2 3 4],'EdgeColor','r','LineWidth',2);

% subplot(1, 2, 2)
% h2=imshow(right_pic);

line2=line(4*rand(1,100),4*rand(1,100));
rect2=rectangle('Position',[1 2 3 4],'EdgeColor','r','LineWidth',2);

%% start the program
tic;

m=5; % number of past points

x=1:m;
y=1:m;
z=1:m;
t=1:m;


LEFT_PICTURES_ARR=zeros(0,0);
LEFT_PIXELS_PAST_ARR=zeros(0,0);
LEFT_BOX_PAST_ARR=zeros(0,0);
LEFT_PIXELS_FUTURE_ARR=zeros(0,0);
LEFT_BOX_FUTURE_ARR=zeros(0,0);
left_pixel_arr=zeros(2,m);

box=50;
left_pixel=[];
right_pixel=[];

i=0;
while(i < 200)
%%
    i=i+1;
    trigger([vid1 , vid2]);
    % Get the snapshot of the current frame
    
    left_pic  = getdata(vid1);
    right_pic = getdata(vid2);
    
    % find the red ball
    [left_pixel  ,  left_box] = fast_find_ball(left_pic  , left_pixel  , box);     
    [right_pixel , right_box] = fast_find_ball(right_pic , right_pixel , 2*box);
    
    set(h1,'cdata',left_pic);
  
    LEFT_PICTURES_ARR{i}=left_pic;
    % if the ball wasn't found
 
    if isempty(left_pixel) || isempty(right_pixel)
        LEFT_PIXELS_FUTURE_ARR{i}=[];       
        left_pixel_arr=zeros(2,m); 
        LEFT_PIXELS_PAST_ARR{i}=left_pixel_arr;
        continue;
    end   
    
    left_pixel_arr=[left_pixel_arr(:,2:m) , left_pixel];
    
    LEFT_PIXELS_PAST_ARR{i} = left_pixel_arr;
    LEFT_BOX_PAST_ARR{i}    = left_box;
    
    set(line1,'xdata',left_pixel_arr(1,1:m),'ydata',left_pixel_arr(2,1:m) ,...
                'LineStyle' ,'-' ,'Marker' ,'+','Color', [0 0 1]);  
    
    set(rect1,'Position',left_box,'EdgeColor','r','LineWidth',2);

    % find the ball cordinate
    [left_cord,right_cord] = stereo_triangulation(left_pixel,right_pixel,om,T,...
                                fc_left,cc_left,kc_left,alpha_c_left,...
                                fc_right,cc_right,kc_right,alpha_c_right);
                            
    x=[x(2:m),left_cord(1)];
    y=[y(2:m),left_cord(2)];  
    z=[z(2:m),left_cord(3)];  
    t=[t(2:m),toc];       
     
    % estimate the tracking
    [XX , YY , ZZ , TT ]=estimate_vector(x,y,z,t);
    
    % convert to pixel in one camera
    pixel=project_points([XX; YY ; ZZ],fc_left,cc_left,kc_left,alpha_c_left);
     
    % delete pixel out of picture
    
    fix_pixel = filter_pixel(pixel);
    LEFT_PIXELS_FUTURE_ARR{i} = fix_pixel;    
    
    if isempty(fix_pixel) % no future
        left_pixel=[];    % for the next picture
        LEFT_BOX_FUTURE_ARR{i} = [];
        continue;
    end
    

    LEFT_BOX_FUTURE_ARR{i}    = [(pixel(1,5)-box) ,(pixel(2,5)-box), 2*box , 2*box];
    
    len = length(fix_pixel(1,:));
    
    % plot the tracking on the picture
 
    set(line2,'xdata',fix_pixel(1,1:len),'ydata',fix_pixel(2,1:len) ,...
                'LineStyle' ,'-' ,'Marker' ,'+','Color', [1 0 1]);          
              
    set(rect2,'Position',LEFT_BOX_FUTURE_ARR{i},'EdgeColor',[0 1 1],'LineWidth',2);
    
    % the new pixel that estimated        
    left_pixel=pixel(:,4);
end

i/toc

% Stop the video aquisition.
stop(vid1);
stop(vid2);

% Flush all the image data stored in the memory buffer.
flushdata(vid1);
flushdata(vid2);

% Clear all variables

sprintf('%s','That was all about Image tracking, Guess that was pretty easy :) ')

% start slow motion
show_pictures;
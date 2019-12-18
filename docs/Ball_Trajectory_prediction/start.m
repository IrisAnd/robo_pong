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

load Calib_Results.mat
addpath('TOOLBOX_calib')

%% start the cameras
start(vid1);
start(vid2);

trigger([vid1 , vid2]);

% Get the snapshot of the current frame
left_pic = getdata(vid1);
right_pic = getdata(vid2);
%% start the program

figure(1);
subplot(1, 2, 1)
h1=imshow(left_pic);

line1=line(4*rand(1,100),4*rand(1,100));
rect1=rectangle('Position',[1 2 3 4],'EdgeColor','r','LineWidth',2);
line2=line(4*rand(1,100),4*rand(1,100));
rect2=rectangle('Position',[1 2 3 4],'EdgeColor','r','LineWidth',2);

line7=line(4*rand(1,100),4*rand(1,100));
line8=line(4*rand(1,100),4*rand(1,100));

subplot(1, 2, 2);
line3=line(4*rand(1,100),4*rand(1,100),4*rand(1,100));
line4=line(4*rand(1,100),4*rand(1,100),4*rand(1,100));

line(0,0,0,'Color', [0 1 0],'Marker' ,'+','LineWidth',20);

axis([-2000 2000 0 6000 -1000 2000]);
grid on

% subplot(1, 2, 2)
% % h2=imshow(right_pic);
% 
% line(0,0,0,'Color', [0 1 0],'Marker' ,'+','LineWidth',20);
% line5=line(4*rand(1,100),4*rand(1,100),4*rand(1,100));
% 
% axis([-2000 2000 0 6000 -1000 2000]);
% grid on

arr_pixels_x=0;
arr_pixels_y=0;
arr_pixels_z=0;




tic;
m=5; % number of past points
time=toc;
t=linspace(time-0.04*m,time,m);


LEFT_PICTURES_ARR=zeros(0,0);
LEFT_PIXELS_PAST_ARR=zeros(0,0);
LEFT_BOX_PAST_ARR=zeros(0,0);
LEFT_PIXELS_FUTURE_ARR=zeros(0,0);
LEFT_BOX_FUTURE_ARR=zeros(0,0);
LEFT_CORD_PAST_VECTOR=zeros(0,0);
LEFT_CORD_FUTURE_VECTOR=zeros(0,0);

RIGHT_PICTURES_ARR=zeros(0,0);

left_last_pixels=[];
right_last_pixels=[];

box=150;
left_pixel=[];
right_pixel=[];

flag=1;
k=1;
i=0;
len1=200;
while(i < len1)    % change it to while 1  for preview real time 
    
    i=mod(i,len1) + 1;   % i=i+1;
    
    % Get the snapshot of the current frame
    trigger([vid1 , vid2]);
    left_pic  = getdata(vid1);
    right_pic = getdata(vid2);
    
    % find the red ball
    [left_pixel  ,  left_box , radius] = fast_find_ball(left_pic  , left_pixel  , box);     
    [right_pixel , right_box] = fast_find_ball(right_pic , right_pixel , box);
    
    set(h1,'cdata',left_pic);
    
    % saving pictures
    LEFT_PICTURES_ARR{i}=left_pic;
    RIGHT_PICTURES_ARR{i}=right_pic;
    
    % if the ball wasn't found at least in one pic
    if isempty(left_pixel) || isempty(right_pixel) 
        LEFT_PIXELS_PAST_ARR{i}=[];
        LEFT_CORD_PAST_VECTOR{i}=[];
        LEFT_PIXELS_FUTURE_ARR{i}=[];
        left_last_pixels=[]; 
        right_last_pixels=[];
        flag=1;
        continue;
    end
    
    % this picture has the ball and picture before does not have the ball
    % this like the first time
    if flag
        left_last_pixels=[];
        right_last_pixels=[];
        for j=1:m
            left_last_pixels  = [left_last_pixels , left_pixel];
            right_last_pixels = [right_last_pixels , right_pixel];
        end
        time=toc;
        t=linspace(time-1*m,time,m);
        flag=0; 
    end
    
    % create 1*m vector for time and motion
    left_last_pixels  = [left_last_pixels(:,2:m) , left_pixel];
    right_last_pixels = [right_last_pixels(:,2:m) , right_pixel];
    t=[t(2:m),toc];
        
    LEFT_PIXELS_PAST_ARR{i} = left_last_pixels;
    LEFT_BOX_PAST_ARR{i}    = left_box;
    
    set(line1,'xdata',left_last_pixels(1,:),'ydata',left_last_pixels(2,:) ,...
                'LineStyle' ,'-' ,'Marker' ,'+','Color', [0 0 1]);  
    
    % plot the detection
    
%     set(rect1,'Position',left_box,'EdgeColor','r','LineWidth',2);
    
    c = -1*radius: radius/20 : 1*radius;
    r = sqrt(radius^2-c.^2);
    set(line7,'xdata',left_pixel(1) + c,'ydata',left_pixel(2) + r ,...
                'LineStyle' ,'-' ,'Marker' ,'.','Color', [0 1 0]);
    set(line8,'xdata',left_pixel(1) + c,'ydata',left_pixel(2) - r ,...
        'LineStyle' ,'-' ,'Marker' ,'+','Color', [0 1 0]);
    


    % find the ball cordinate
    [left_cord,right_cord] = stereo_triangulation(left_last_pixels,right_last_pixels,om,T,...
                                fc_left ,cc_left ,kc_left ,alpha_c_left,...
                                fc_right,cc_right,kc_right,alpha_c_right);
    
    
    set(line3,'xdata',left_cord(1,:),'ydata',left_cord(3,:) ,...
                'zdata',-left_cord(2,:),'LineStyle' ,'-' ,'Marker' ,'+','Color', [0 0 1]);
                            
    LEFT_CORD_PAST_VECTOR{i}=left_cord;
    
    % estimate the tracking
    
    left_vector=estimate_vector3(left_cord,t,50);
    right_vector=estimate_vector3(right_cord,t,20);
    
    set(line4,'xdata',left_vector(1,:),'ydata',left_vector(3,:) ,...
                'zdata',-left_vector(2,:),'LineStyle','-','Marker' ,'+','Color', [1 0 1]);
    
    LEFT_CORD_FUTURE_VECTOR{i}=left_vector;
    
    % plot past this is in show pictures
    
%     arr_pixels_x(i)=left_cord(1,m);
%     arr_pixels_y(i)=left_cord(3,m);
%     arr_pixels_z(i)=left_cord(2,m);
%     
%     
%     start_sh = (i-50)*((i-50)>0)+1;
%     set(line5,'xdata',arr_pixels_x(start_sh:i),'ydata',arr_pixels_y(start_sh:i) ,...
%             'zdata',-arr_pixels_z(start_sh:i),'LineStyle' ,'-' ,'Marker' ,'.'...
%             ,'LineWidth',5,'Color', [1 0 0]);
    
    % convert to pixel in one camera
    
    new_left_pixels  = project_points(left_vector,fc_left,cc_left,kc_left,alpha_c_left);
    new_right_pixels = project_points(right_vector,fc_right,cc_right,kc_right,alpha_c_right); 
    
    % delete pixel out of picture
    
    fix_left_pixels = filter_pixel(new_left_pixels);
    LEFT_PIXELS_FUTURE_ARR{i} = fix_left_pixels; 
    
    fix_right_pixels = filter_pixel(new_right_pixels);
    
    if isempty(fix_left_pixels) || isempty(fix_right_pixels)  % no future
        left_pixel=[];    % for the next picture
        right_pixel=[];    % for the next picture
        LEFT_BOX_FUTURE_ARR{i} = [];
        continue;
    end
 
    % the new pixel that estimated
    len_left = length(fix_left_pixels(1,:));
    len_right = length(fix_right_pixels(1,:));
    num_pixel=5;
    left_pixel  = fix_left_pixels(:,num_pixel*(num_pixel<len_left) + 1);
    right_pixel = fix_right_pixels(:,num_pixel*(num_pixel<len_right) + 1);
    
    temp_box = small_pic(left_pixel , box);
    
    left_box_future = [temp_box(:,1) ; temp_box(:,2) - temp_box(:,1)];
    LEFT_BOX_FUTURE_ARR{i} = left_box_future;
       
    % plot the tracking on the picture
 
    set(line2,'xdata',fix_left_pixels(1,:),'ydata',fix_left_pixels(2,:) ,...
                'LineStyle' ,'-' ,'Marker' ,'+','Color', [1 0 1]);          
              
    set(rect2,'Position',left_box_future,'EdgeColor',[0 1 1],'LineWidth',2);
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
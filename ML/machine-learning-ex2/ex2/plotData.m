function plotData(X, y)
%PLOTDATA Plots the data points X and y into a new figure 
%   PLOTDATA(x,y) plots the data points with + for the positive examples
%   and o for the negative examples. X is assumed to be a Mx2 matrix.

% Create New Figure
figure; hold on;

% ====================== YOUR CODE HERE ======================
% Instructions: Plot the positive and negative examples on a
%               2D plot, using the option 'k+' for the positive
%               examples and 'ko' for the negative examples.
%

Z=horzcat(X, y);
iP = Z(:,3)>0; 
iN = Z(:,3)==0;
ZP = Z(iP,:);
ZN = Z(iN,:);

plot(ZP(:,1),ZP(:,2),'k+');
plot(ZN(:,1),ZN(:,2),'ko');


% =========================================================================



hold off;

end

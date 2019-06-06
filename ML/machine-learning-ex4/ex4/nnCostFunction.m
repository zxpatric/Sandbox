function [J grad] = nnCostFunction(nn_params, ...
                                   input_layer_size, ...
                                   hidden_layer_size, ...
                                   num_labels, ...
                                   X, y, lambda)
%NNCOSTFUNCTION Implements the neural network cost function for a two layer
%neural network which performs classification
%   [J grad] = NNCOSTFUNCTON(nn_params, hidden_layer_size, num_labels, ...
%   X, y, lambda) computes the cost and gradient of the neural network. The
%   parameters for the neural network are "unrolled" into the vector
%   nn_params and need to be converted back into the weight matrices. 
% 
%   The returned parameter grad should be a "unrolled" vector of the
%   partial derivatives of the neural network.
%

% Reshape nn_params back into the parameters Theta1 and Theta2, the weight matrices
% for our 2 layer neural network
Theta1 = reshape(nn_params(1:hidden_layer_size * (input_layer_size + 1)), ...
                 hidden_layer_size, (input_layer_size + 1));

Theta2 = reshape(nn_params((1 + (hidden_layer_size * (input_layer_size + 1))):end), ...
                 num_labels, (hidden_layer_size + 1));

% Setup some useful variables
m = size(X, 1);
         
% You need to return the following variables correctly 
J = 0;
Theta1_grad = zeros(size(Theta1));
Theta2_grad = zeros(size(Theta2));

% ====================== YOUR CODE HERE ======================
% Instructions: You should complete the code by working through the
%               following parts.
%
% Part 1: Feedforward the neural network and return the cost in the
%         variable J. After implementing Part 1, you can verify that your
%         cost function computation is correct by verifying the cost
%         computed in ex4.m

X = [ones(m, 1) X];

z2 = X*Theta1';
az2 = sigmoid(z2);
a2 = [ones(size(az2,1),1) az2];

z3 = a2*Theta2';
az3 = sigmoid(z3);
% a3 = [ones(size(az3,1),1) az3];

J1 = 0;
k=size(az3,2);
yy = zeros(m,k);
for i=1:m
    yi = y(i);
    yy(i, yi)=1;
    for j=1:k
        yj=(yi==j);
        hx = az3(i,j);
        J1 = J1 + yj*log(hx)+(1-yj)*log(1-hx);
    end
end

J2 = 0;
Theta1_ = Theta1(:,2:end);
Theta2_ = Theta2(:,2:end);
J2 = trace(Theta1_*Theta1_') + trace(Theta2_*Theta2_');

om = 1/m;
J = -om*J1+lambda*om*0.5*J2;


% Part 2: Implement the backpropagation algorithm to compute the gradients
%         Theta1_grad and Theta2_grad. You should return the partial derivatives of
%         the cost function with respect to Theta1 and Theta2 in Theta1_grad and
%         Theta2_grad, respectively. After implementing Part 2, you can check
%         that your implementation is correct by running checkNNGradients
%
%         Note: The vector y passed into the function is a vector of labels
%               containing values from 1..K. You need to map this vector into a 
%               binary vector of 1's and 0's to be used with the neural network
%               cost function.
%
%         Hint: We recommend implementing backpropagation using a for-loop
%               over the training examples if you are implementing it for the 
%               first time.
%


diff3 = az3 - yy;
diff2 = diff3*Theta2.*(a2.*(1-a2));
dif2 = diff2(:,2:end);

delta2=diff3'*a2;
delta1=dif2'*X;


% Part 3: Implement regularization with the cost function and gradients.
%
%         Hint: You can implement this around the code for
%               backpropagation. That is, you can compute the gradients for
%               the regularization separately and then add them to Theta1_grad
%               and Theta2_grad from Part 2.
%

Theta2_0 = [zeros(size(Theta2_,1),1), Theta2_];
Theta1_0 = [zeros(size(Theta1_,1),1), Theta1_];

Theta2_grad = om*delta2 + om*lambda*Theta2_0;
Theta1_grad = om*delta1 + om*lambda*Theta1_0;


% -------------------------------------------------------------

% =========================================================================

% Unroll gradients
grad = [Theta1_grad(:) ; Theta2_grad(:)];


end

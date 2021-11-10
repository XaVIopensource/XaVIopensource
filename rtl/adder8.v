/////////////////////////////////////////////////////////
// 8-bit adder (generic)
/////////////////////////////////////////////////////////

// Alternative to the Brent-Kung adder.
// Adder to allow synthesis tool to choose the best adder implementation.

module adder8(A, B, CI, S, CO);
  input [7:0]	A;
  input [7:0]	B;
  output [7:0] S;
 
  // top and tail bits to accomodate carrys in and out
  assign sum = { 1'b0, A,   CI } +  { 1'b0, B, 1'b0 };

  assign S  = sum[8:1];
  assign CO = sum[9];
endmodule

# River log carry input responsiveness

The four-step carry animation blocked the main input loop for approximately 100ms plus LCD drawing time. It now polls Keys.pressed() during each substep and buffers the first directional press. After the carry completes, the normal movement handler processes the buffered input. This preserves normal tree and water collision checks. One press is buffered, not an unbounded queue; pause and reset inputs are not buffered during animation. Hardware verification is required.

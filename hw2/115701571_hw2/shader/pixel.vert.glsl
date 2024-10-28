#version 410 core

layout (location = 0) in vec2 aPosition;
layout (location = 1) in vec3 aColor;

out vec3 ourColor;

uniform float windowWidth;
uniform float windowHeight;
uniform float pixelSize;  // New uniform for pixel size

void main()
{
    vec2 transformedPosition = vec2(2.0f * aPosition.x / windowWidth - 1.0f,
                                    2.0f * aPosition.y / windowHeight - 1.0f);
    
    gl_Position = vec4(transformedPosition, 0.0f, 1.0f);
    gl_PointSize = pixelSize;  // Set the size of the point
    ourColor = aColor;
}

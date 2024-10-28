#version 410 core

out vec4 fragColor;

uniform vec4 bezierColor;

void main()
{
    fragColor = bezierColor;
}

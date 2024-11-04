#version 410 core

out vec4 fragColor;

uniform vec4 splineColor;

void main()
{
    fragColor = splineColor;
}

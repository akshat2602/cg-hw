#version 410 core
layout (location = 0) in vec2 aPos;

uniform float windowWidth;
uniform float windowHeight;

void main()
{
    vec2 normalizedPos = vec2(
        2.0 * aPos.x / windowWidth - 1.0,
        2.0 * aPos.y / windowHeight - 1.0
    );
    gl_Position = vec4(normalizedPos, 0.0, 1.0);
}

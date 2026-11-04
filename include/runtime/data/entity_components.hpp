#pragma once
#include <se_export.hpp>
#include <cstdint>

enum class Type : uint8_t {
    Value,
    Number,
    String,
    Boolean,
    Color
};

struct SE_EXPORT RenderInfo {
#ifdef __XBOX__
    float renderX = 0.0f;
    float renderY = 0.0f;
    float renderScaleX = 1.0f;
    float renderScaleY = 1.0f;
    float renderRotation = 0.0f;

    double oldX = -999999.0;
    double oldY = -999999.0;
    float oldSize = -999999.0f;
    float oldRotation = -999999.0f;
    struct {
        bool valid = false;
        bool isSVG = false, halfQuality = false;
        int rotationStyle = -1, bitmapResolution = 0;
        int imageWidth = 0, imageHeight = 0;
        double centerX = 0, centerY = 0;
        int screenWidth = 0, screenHeight = 0;
        int projectWidth = 0, projectHeight = 0, renderMode = -1;
        float renderScale = 0;
    } xboxTransform;
#else
    float renderX;
    float renderY;
    float renderScaleX;
    float renderScaleY;
    float renderRotation;

    float oldX, oldY;
    float oldSize, oldRotation;
#endif
    int oldCostumeID = -1;
    bool forceUpdate = false;
};

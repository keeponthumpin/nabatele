// object_pose_wind — GLSL POP (point class), 1 point out.
// P = object centre (mm), rot = tilt from cables (vec3 rad).
// Combines: tether-driven centre/tilt + wind pendulum swing (master file §5).
//
// Uniforms:
//   uTetherA..D : vec3 (cur,min,max) METRES
//   uAnchorA..D : vec3 winch world pos (mm)
//   uWind       : vec4 (dirX,dirY,dirZ, speed_m/s)  -- dir = "blows toward", normalized
//   uUnitsPerMetre : float (1000.0)
// Output attributes: P (vec4), rot (vec3)

const float Fz = 785.0;     // N, net buoyancy
const float K  = 33.44;     // N/(m/s)^2, drag coeff
const float Lp = 35.7;      // m, effective pendulum length
const float RAD2DEG = 57.295779513;

void main()
{
    const uint id = TDIndex();
    if (id >= TDNumElements()) return;

    float LA = clamp(uTetherA.x, uTetherA.y, uTetherA.z) * uUnitsPerMetre;
    float LB = clamp(uTetherB.x, uTetherB.y, uTetherB.z) * uUnitsPerMetre;
    float LC = clamp(uTetherC.x, uTetherC.y, uTetherC.z) * uUnitsPerMetre;
    float LD = clamp(uTetherD.x, uTetherD.y, uTetherD.z) * uUnitsPerMetre;

    vec3 pA = uAnchorA + vec3(0.0, LA, 0.0);
    vec3 pB = uAnchorB + vec3(0.0, LB, 0.0);
    vec3 pC = uAnchorC + vec3(0.0, LC, 0.0);
    vec3 pD = uAnchorD + vec3(0.0, LD, 0.0);

    vec3 centre = (pA + pB + pC + pD) * 0.25;

    const float halff = 4000.0;
    float roll  = atan(((pC.y + pD.y) - (pA.y + pB.y)) * 0.5, 2.0 * halff);
    float pitch = atan(((pB.y + pD.y) - (pA.y + pC.y)) * 0.5, 2.0 * halff);

    float v = uWind.w;
    float vClamped = min(v, 5.0);
    float Fdrag = K * vClamped * vClamped;
    float theta = atan(Fdrag / Fz);

    vec3 windDir = vec3(uWind.x, 0.0, uWind.z);
    float wlen = length(windDir);
    windDir = (wlen > 1e-6) ? windDir / wlen : vec3(0.0);

    float horiz = Lp * sin(theta) * uUnitsPerMetre;
    float drop  = -Lp * (1.0 - cos(theta)) * uUnitsPerMetre;

    centre += windDir * horiz + vec3(0.0, drop, 0.0);

    P[id]   = vec3(centre);
    rot[id] = vec3(pitch * RAD2DEG, 0.0, roll * RAD2DEG);
}
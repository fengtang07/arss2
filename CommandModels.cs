// CommandModels.cs
//
// Defines the C# classes that represent the JSON data structures sent by the Python agent.
// These classes are used by Unity's JsonUtility to parse the incoming requests.

using System;

namespace ARSS.API
{
    [Serializable]
    public class SpawnPayload
    {
        public string object_name;
        public Position position;
        public Scale scale;
        public ColorData color;
    }

    [Serializable]
    public class LightingPayload
    {
        public string preset;
    }
    
    [Serializable]
    public class AttachScriptPayload
    {
        public string object_name;
        public string script_name;
    }

    [Serializable]
    public class Position
    {
        public float x;
        public float y;
        public float z;
    }

    [Serializable]
    public class Scale
    {
        public float x = 1f;
        public float y = 1f;
        public float z = 1f;
    }

    [Serializable]
    public class ColorData
    {
        public float r = 1f;
        public float g = 1f;
        public float b = 1f;
    }

    [Serializable]
    public class ApiResponse
    {
        public bool success;
        public string message;
    }
} 
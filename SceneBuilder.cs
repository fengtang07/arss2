// SceneBuilder.cs
//
// This script contains the core logic for manipulating the Unity scene.
// It has public methods that can be called to spawn primitives, change their
// properties (like color and scale), and clear the scene.
//
// This component should be attached to a GameObject in your Unity scene,
// for example, an empty GameObject named "SceneManager".

using UnityEngine;
using System.Collections.Generic; // Required for using List

public class SceneBuilder : MonoBehaviour
{
    // A list to keep track of all the objects we spawn.
    // This is useful for clearing the scene later.
    private List<GameObject> spawnedObjects = new List<GameObject>();

    /// <summary>
    /// Creates a primitive GameObject at a specified position, scale, and color.
    /// </summary>
    /// <param name="objectName">The type of primitive to spawn (e.g., "Cube", "Sphere").</param>
    /// <param name="position">The world position to spawn the object.</param>
    /// <param name="scale">The local scale of the new object.</param>
    /// <param name="color">The color of the new object's material.</param>
    public void SpawnObject(string objectName, Vector3 position, Vector3 scale, Color color)
    {
        PrimitiveType primitiveType;

        // Use a switch statement to parse the object name string into a Unity PrimitiveType.
        // This is safer than Enum.Parse because it handles potential errors gracefully.
        switch (objectName.ToLower())
        {
            case "cube":
                primitiveType = PrimitiveType.Cube;
                break;
            case "sphere":
                primitiveType = PrimitiveType.Sphere;
                break;
            case "capsule":
                primitiveType = PrimitiveType.Capsule;
                break;
            case "cylinder":
                primitiveType = PrimitiveType.Cylinder;
                break;
            case "plane":
                primitiveType = PrimitiveType.Plane;
                break;
            default:
                // If the name is not recognized, log an error and do nothing.
                Debug.LogError($"[SceneBuilder] Unknown primitive type: {objectName}");
                return;
        }

        // Create the primitive GameObject.
        GameObject newObject = GameObject.CreatePrimitive(primitiveType);
        newObject.name = $"Generated_{objectName}";

        // Set the object's position and scale.
        newObject.transform.position = position;
        newObject.transform.localScale = scale;

        // To set the color, we need to access the object's Renderer component
        // and create a new Material instance for it.
        Renderer renderer = newObject.GetComponent<Renderer>();
        if (renderer != null)
        {
            // By creating a new material, we ensure that changing the color of this object
            // does not affect other objects that might share the default material.
            Material materialInstance = new Material(renderer.material);
            materialInstance.color = color;
            renderer.material = materialInstance;
        }

        // Add the newly created object to our list for tracking.
        spawnedObjects.Add(newObject);

        Debug.Log($"[SceneBuilder] Spawned {objectName} at {position}");
    }

    /// <summary>
    /// Destroys all GameObjects that were previously spawned by this script.
    /// </summary>
    public void ClearScene()
    {
        Debug.Log($"[SceneBuilder] Clearing scene, destroying {spawnedObjects.Count} objects.");

        // Iterate through the list of spawned objects and destroy each one.
        foreach (GameObject obj in spawnedObjects)
        {
            // It's good practice to check if the object hasn't already been destroyed.
            if (obj != null)
            {
                Destroy(obj);
            }
        }

        // Clear the list itself after destroying the objects.
        spawnedObjects.Clear();
    }
}

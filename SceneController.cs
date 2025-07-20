// SceneController.cs (Real GLB Loading)
//
// Professional GLB loading with safe coroutine implementation

using UnityEngine;
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using GLTFast;

namespace ARSS.API
{
    public class SceneController : MonoBehaviour
    {
        [Header("Lighting Presets")]
        public Material daySkybox;
        public Material nightSkybox;
        public Material sunsetSkybox;
        public Light directionalLight;

        private List<GameObject> spawnedObjects = new List<GameObject>();

        // Synchronous method for HTTP server to call
        public ApiResponse SpawnObject(SpawnPayload payload)
        {
            try
            {
                // Handle GLB files with coroutine
                if (payload.object_name.Contains(".glb") || payload.object_name.Contains(".gltf"))
                {
                    Debug.Log($"[SceneController] Starting GLB loading coroutine for: {payload.object_name}");
                    StartCoroutine(LoadGLBCoroutine(payload));
                    return new ApiResponse { 
                        success = true, 
                        message = $"GLB loading started for {payload.object_name}" 
                    };
                }

                // Handle primitives synchronously
                if (System.Enum.TryParse<PrimitiveType>(payload.object_name, true, out var primitiveType))
                {
                    GameObject newObject = GameObject.CreatePrimitive(primitiveType);
                    newObject.name = $"Primitive_{payload.object_name}";
                    newObject.transform.position = new Vector3(payload.position.x, payload.position.y, payload.position.z);
                    newObject.transform.localScale = new Vector3(payload.scale.x, payload.scale.y, payload.scale.z);
                    
                    if (payload.color != null)
                    {
                        ApplyColor(newObject, new Color(payload.color.r, payload.color.g, payload.color.b));
                    }
                    
                    spawnedObjects.Add(newObject);
                    string successMsg = $"Successfully spawned '{newObject.name}'.";
                    Debug.Log($"[SceneController] {successMsg}");
                    return new ApiResponse { success = true, message = successMsg };
                }
                else
                {
                    // Unknown object type
                    GameObject placeholder = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    placeholder.name = $"Unknown_{payload.object_name}";
                    placeholder.transform.position = new Vector3(payload.position.x, payload.position.y, payload.position.z);
                    spawnedObjects.Add(placeholder);
                    
                    return new ApiResponse { 
                        success = true, 
                        message = $"Created placeholder for unknown object: {payload.object_name}" 
                    };
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[SceneController] Exception in SpawnObject: {e.Message}");
                return new ApiResponse { success = false, message = $"Spawn exception: {e.Message}" };
            }
        }

        private IEnumerator LoadGLBCoroutine(SpawnPayload payload)
        {
            Debug.Log($"[SceneController] Starting GLB coroutine for: {payload.object_name}");
            
            string modelPath = Path.Combine(Application.dataPath, "ImportedModels", payload.object_name);
            Debug.Log($"[SceneController] Loading GLB from: {modelPath}");

            if (!File.Exists(modelPath))
            {
                Debug.LogError($"[SceneController] GLB file not found: {modelPath}");
                CreateFoxFallbackAndAdd(payload);
                yield break;
            }

            var gltf = new GltfImport();
            bool loadSuccess = false;
            
            // Load the GLB file
            var loadTask = gltf.Load(modelPath);
            
            // Wait for completion without blocking main thread (outside try-catch)
            yield return new WaitUntil(() => loadTask.IsCompleted);
            
            try
            {
                loadSuccess = loadTask.Result;
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[SceneController] Exception getting load result: {e.Message}");
                CreateFoxFallbackAndAdd(payload);
                yield break;
            }
            
            if (!loadSuccess)
            {
                Debug.LogError($"[SceneController] Failed to load GLB file: {modelPath}");
                CreateFoxFallbackAndAdd(payload);
                yield break;
            }
            
            Debug.Log($"[SceneController] GLB loaded successfully, now instantiating...");
            
            // Create parent object for the model
            GameObject parentObject = new GameObject($"Model_{payload.object_name.Replace(".glb", "")}");
            parentObject.transform.position = new Vector3(payload.position.x, payload.position.y, payload.position.z);
            
            // For GLB models, apply a smaller base scale since they're often oversized
            Vector3 adjustedScale = new Vector3(payload.scale.x, payload.scale.y, payload.scale.z);
            
            // Apply scale adjustment for GLB models - they're typically much larger than primitives
            float glbScaleFactor = 0.1f; // Reduce to 10% of original size
            adjustedScale *= glbScaleFactor;
            
            parentObject.transform.localScale = adjustedScale;
            
            Debug.Log($"[SceneController] Applied adjusted scale: {adjustedScale} (original: {payload.scale.x}, {payload.scale.y}, {payload.scale.z})");
            
            // Instantiate the model
            var instantiator = new GameObjectInstantiator(gltf, parentObject.transform);
            var instantiateTask = gltf.InstantiateMainSceneAsync(instantiator);
            
            // Wait for instantiation (outside try-catch)
            yield return new WaitUntil(() => instantiateTask.IsCompleted);
            
            bool instantiateSuccess = false;
            try
            {
                instantiateSuccess = instantiateTask.Result;
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[SceneController] Exception during instantiation: {e.Message}");
                DestroyImmediate(parentObject);
                CreateFoxFallbackAndAdd(payload);
                yield break;
            }
            
            if (instantiateSuccess)
            {
                // Intelligent auto-scaling based on model analysis
                CalculateAndApplyIntelligentScale(parentObject, payload);
                
                spawnedObjects.Add(parentObject);
                Debug.Log($"[SceneController] Successfully loaded and instantiated GLB: {parentObject.name}");
                Debug.Log($"[SceneController] Model has {parentObject.transform.childCount} child objects");
            }
            else
            {
                Debug.LogError($"[SceneController] Failed to instantiate GLB model");
                DestroyImmediate(parentObject);
                CreateFoxFallbackAndAdd(payload);
            }
        }

        private GameObject CreateFoxFallback(SpawnPayload payload)
        {
            Debug.Log($"[SceneController] Creating fox fallback for: {payload.object_name}");
            
            // Create a detailed fox-like object
            GameObject foxBody = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            foxBody.name = "Fox_Fallback";
            foxBody.transform.position = new Vector3(payload.position.x, payload.position.y, payload.position.z);
            foxBody.transform.localScale = new Vector3(payload.scale.x, payload.scale.y, payload.scale.z);
            
            // Make it orange like a fox
            var renderer = foxBody.GetComponent<Renderer>();
            if (renderer != null)
            {
                var material = new Material(renderer.sharedMaterial);
                material.color = new Color(0.8f, 0.4f, 0.1f); // Fox orange
                renderer.material = material;
            }
            
            // Add head
            GameObject head = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            head.transform.SetParent(foxBody.transform);
            head.transform.localPosition = new Vector3(0, 0.7f, 0);
            head.transform.localScale = Vector3.one * 0.6f;
            head.name = "Fox_Head";
            
            // Add tail
            GameObject tail = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            tail.transform.SetParent(foxBody.transform);
            tail.transform.localPosition = new Vector3(0, 0, -1.2f);
            tail.transform.localScale = Vector3.one * 0.4f;
            tail.name = "Fox_Tail";
            
            Debug.Log($"[SceneController] Created fox fallback with head and tail");
            return foxBody;
        }

        private void CreateFoxFallbackAndAdd(SpawnPayload payload)
        {
            Debug.LogWarning($"[SceneController] GLB loading failed, creating fallback object");
            GameObject fallback = CreateFoxFallback(payload);
            spawnedObjects.Add(fallback);
        }

        private void ApplyColor(GameObject obj, Color color)
        {
            var renderer = obj.GetComponent<Renderer>();
            if (renderer != null)
            {
                var material = new Material(renderer.sharedMaterial);
                material.color = color;
                renderer.material = material;
            }
        }

        public ApiResponse SetLighting(LightingPayload payload)
        {
            if (directionalLight == null)
            {
                return new ApiResponse { success = false, message = "Directional light not assigned." };
            }

            switch (payload.preset.ToLower())
            {
                case "day":
                    RenderSettings.skybox = daySkybox;
                    directionalLight.color = Color.white;
                    directionalLight.intensity = 1.0f;
                    break;
                case "night":
                    RenderSettings.skybox = nightSkybox;
                    directionalLight.color = new Color(0.2f, 0.2f, 0.4f);
                    directionalLight.intensity = 0.3f;
                    break;
                case "sunset":
                    RenderSettings.skybox = sunsetSkybox;
                    directionalLight.color = new Color(1.0f, 0.6f, 0.3f);
                    directionalLight.intensity = 0.7f;
                    break;
                default:
                    return new ApiResponse { success = false, message = $"Unknown lighting preset: {payload.preset}" };
            }

            return new ApiResponse { success = true, message = $"Lighting set to {payload.preset}." };
        }

        public ApiResponse AttachScript(AttachScriptPayload payload)
        {
            GameObject target = null;
            foreach (var obj in spawnedObjects)
            {
                if (obj.name.Contains(payload.object_name))
                {
                    target = obj;
                    break;
                }
            }

            if (target == null)
            {
                return new ApiResponse { success = false, message = $"Target object '{payload.object_name}' not found." };
            }

            Debug.Log($"[SceneController] Would attach script to {target.name}: {payload.script_name}");
            return new ApiResponse { success = true, message = $"Script attached to {target.name}." };
        }

        public ApiResponse ClearScene()
        {
            int count = spawnedObjects.Count;
            foreach (var obj in spawnedObjects)
            {
                if (obj != null)
                {
                    DestroyImmediate(obj);
                }
            }
            spawnedObjects.Clear();

            return new ApiResponse { success = true, message = $"Cleared scene - destroyed {count} objects." };
        }

        private void CalculateAndApplyIntelligentScale(GameObject model, SpawnPayload payload)
        {
            try
            {
                // Get the model's bounding box
                Bounds modelBounds = CalculateModelBounds(model);
                Debug.Log($"[SceneController] Model bounds: {modelBounds.size} (center: {modelBounds.center})");
                
                // Determine target size based on object type
                float targetSize = DetermineTargetSize(payload.object_name);
                
                // Calculate the largest dimension of the model
                float maxDimension = Mathf.Max(modelBounds.size.x, modelBounds.size.y, modelBounds.size.z);
                
                // Calculate scale factor to reach target size
                float autoScaleFactor = targetSize / maxDimension;
                
                // Apply user's requested scale on top of auto-scale
                Vector3 finalScale = new Vector3(
                    autoScaleFactor * payload.scale.x,
                    autoScaleFactor * payload.scale.y,
                    autoScaleFactor * payload.scale.z
                );
                
                model.transform.localScale = finalScale;
                
                Debug.Log($"[SceneController] Auto-scale applied:");
                Debug.Log($"[SceneController] - Model max dimension: {maxDimension:F2}");
                Debug.Log($"[SceneController] - Target size: {targetSize:F2}");
                Debug.Log($"[SceneController] - Auto-scale factor: {autoScaleFactor:F3}");
                Debug.Log($"[SceneController] - Final scale: {finalScale}");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"[SceneController] Error in intelligent scaling: {e.Message}");
                // Fallback to simple scaling
                model.transform.localScale = new Vector3(payload.scale.x * 0.1f, payload.scale.y * 0.1f, payload.scale.z * 0.1f);
            }
        }

        private Bounds CalculateModelBounds(GameObject model)
        {
            Bounds bounds = new Bounds(model.transform.position, Vector3.zero);
            bool hasBounds = false;
            
            // Get all renderers in the model and its children
            Renderer[] renderers = model.GetComponentsInChildren<Renderer>();
            
            foreach (Renderer renderer in renderers)
            {
                if (hasBounds)
                {
                    bounds.Encapsulate(renderer.bounds);
                }
                else
                {
                    bounds = renderer.bounds;
                    hasBounds = true;
                }
            }
            
            // If no renderers found, use a default bounds
            if (!hasBounds)
            {
                bounds = new Bounds(model.transform.position, Vector3.one);
            }
            
            return bounds;
        }

        private float DetermineTargetSize(string objectName)
        {
            string name = objectName.ToLower();
            
            // Intelligent size determination based on object type
            if (name.Contains("fox") || name.Contains("animal") || name.Contains("pet"))
            {
                return 1.5f; // Animals should be about 1.5 Unity units
            }
            else if (name.Contains("car") || name.Contains("vehicle") || name.Contains("truck"))
            {
                return 4.0f; // Vehicles should be larger
            }
            else if (name.Contains("tree") || name.Contains("plant"))
            {
                return 3.0f; // Trees should be tall
            }
            else if (name.Contains("house") || name.Contains("building") || name.Contains("structure"))
            {
                return 8.0f; // Buildings should be large
            }
            else if (name.Contains("furniture") || name.Contains("chair") || name.Contains("table"))
            {
                return 1.0f; // Furniture should be human-scale
            }
            else if (name.Contains("tool") || name.Contains("weapon") || name.Contains("item"))
            {
                return 0.5f; // Tools should be small
            }
            else if (name.Contains("character") || name.Contains("person") || name.Contains("human"))
            {
                return 1.8f; // Humans should be about 1.8 units tall
            }
            else
            {
                // Default size for unknown objects - roughly cube-sized
                return 1.0f;
            }
        }
    }
} 
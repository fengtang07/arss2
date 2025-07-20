// HttpServer.cs (Simplified Fix)
//
// Back to basics - simpler threading that definitely works

using UnityEngine;
using System;
using System.IO;
using System.Net;
using System.Threading;
using System.Collections.Generic;

namespace ARSS.API
{
    public class HttpServer : MonoBehaviour
    {
        private HttpListener listener;
        private Thread listenerThread;
        private SceneController sceneController;
        private readonly Queue<System.Action> commandQueue = new Queue<System.Action>();

        void Start()
        {
            sceneController = GetComponent<SceneController>();
            if (sceneController == null)
            {
                Debug.LogError("[HttpServer] SceneController component not found.");
                return;
            }

            listener = new HttpListener();
            listener.Prefixes.Add("http://127.0.0.1:8080/");
            listener.Start();
            
            listenerThread = new Thread(StartListener);
            listenerThread.IsBackground = true;
            listenerThread.Start();
            
            Debug.Log("[HttpServer] Server started on http://127.0.0.1:8080/");
        }

        void Update()
        {
            // Process commands on the main thread
            lock (commandQueue)
            {
                while (commandQueue.Count > 0)
                {
                    try
                    {
                        commandQueue.Dequeue().Invoke();
                    }
                    catch (Exception e)
                    {
                        Debug.LogError($"[HttpServer] Error executing command: {e.Message}");
                    }
                }
            }
        }

        private void StartListener()
        {
            while (true)
            {
                try
                {
                    var context = listener.GetContext();
                    ProcessRequest(context);
                }
                catch (Exception e) { Debug.LogError($"[HttpServer] Listener thread error: {e.Message}"); }
            }
        }

        private void ProcessRequest(HttpListenerContext context)
        {
            var request = context.Request;
            string endpoint = request.Url.AbsolutePath.Trim('/');
            string requestBody;

            using (var reader = new StreamReader(request.InputStream, request.ContentEncoding))
            {
                requestBody = reader.ReadToEnd();
            }
            
            Debug.Log($"[HttpServer] Received request for endpoint '{endpoint}'");

            // Queue up the action to be executed on the main thread
            lock (commandQueue)
            {
                commandQueue.Enqueue(() => {
                    HandleEndpoint(endpoint, requestBody, context);
                });
            }
        }

        private void HandleEndpoint(string endpoint, string requestBody, HttpListenerContext context)
        {
            Debug.Log($"[HttpServer] Processing endpoint: {endpoint}");
            
            ApiResponse response;
            
            switch (endpoint)
            {
                case "spawn":
                    var spawnPayload = JsonUtility.FromJson<SpawnPayload>(requestBody);
                    Debug.Log($"[HttpServer] Spawn request for: {spawnPayload.object_name}");
                    
                    // Call SceneController directly - it handles GLB coroutines internally
                    response = sceneController.SpawnObject(spawnPayload);
                    Debug.Log($"[HttpServer] Spawn response: {response.message}");
                    break;

                case "clear_scene":
                    Debug.Log($"[HttpServer] Processing clear scene");
                    response = sceneController.ClearScene();
                    break;

                case "set_lighting":
                    var lightingPayload = JsonUtility.FromJson<LightingPayload>(requestBody);
                    response = sceneController.SetLighting(lightingPayload);
                    break;

                default:
                    response = new ApiResponse { success = false, message = "Invalid endpoint." };
                    break;
            }
            
            SendResponse(context, response);
        }

        private void SendResponse(HttpListenerContext context, ApiResponse payload)
        {
            try
            {
                var response = context.Response;
                response.StatusCode = payload.success ? (int)HttpStatusCode.OK : (int)HttpStatusCode.BadRequest;
                response.ContentType = "application/json";
                string jsonResponse = JsonUtility.ToJson(payload);
                byte[] buffer = System.Text.Encoding.UTF8.GetBytes(jsonResponse);
                response.ContentLength64 = buffer.Length;
                response.OutputStream.Write(buffer, 0, buffer.Length);
                response.OutputStream.Close();
                Debug.Log($"[HttpServer] Response sent: {jsonResponse}");
            }
            catch (Exception e)
            {
                Debug.LogError($"[HttpServer] Could not send response: {e.Message}");
            }
        }

        void OnApplicationQuit()
        {
            if (listener != null && listener.IsListening) listener.Stop();
            if (listenerThread != null && listenerThread.IsAlive) listenerThread.Abort();
        }
    }
}


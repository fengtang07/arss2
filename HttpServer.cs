// HttpServer.cs (Upgraded for VLM & Two-Way Communication)

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
        private readonly Queue<Action> commandQueue = new Queue<Action>();

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
            
            Debug.Log("[HttpServer] Upgraded Server started on http://127.0.0.1:8080/");
        }

        void Update()
        {
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
            while (listener.IsListening)
            {
                try
                {
                    var context = listener.GetContext();
                    // Enqueue the request to be processed on the main thread
                    lock (commandQueue)
                    {
                        commandQueue.Enqueue(() => ProcessRequest(context));
                    }
                }
                catch (Exception e) { Debug.LogError($"[HttpServer] Listener thread error: {e.Message}"); }
            }
        }

        private void ProcessRequest(HttpListenerContext context)
        {
            var request = context.Request;
            string endpoint = request.Url.AbsolutePath.Trim('/');
            string requestBody = "";

            if (request.HasEntityBody)
            {
                using (var reader = new StreamReader(request.InputStream, request.ContentEncoding))
                {
                    requestBody = reader.ReadToEnd();
                }
            }
            
            Debug.Log($"[HttpServer] Received request for endpoint '{endpoint}'");

            ApiResponse responsePayload;

            switch (endpoint)
            {
                case "spawn":
                    var spawnPayload = JsonUtility.FromJson<SpawnPayload>(requestBody);
                    responsePayload = sceneController.SpawnObject(spawnPayload);
                    break;
                case "clear_scene":
                    responsePayload = sceneController.ClearScene();
                    break;
                case "set_lighting":
                    var lightingPayload = JsonUtility.FromJson<LightingPayload>(requestBody);
                    responsePayload = sceneController.SetLighting(lightingPayload);
                    break;
                // *** NEW: Vision Endpoint ***
                case "capture_vision":
                    responsePayload = sceneController.CaptureVision();
                    break;
                // *** NEW: Simulation Endpoint ***
                case "run_simulation":
                    var simPayload = JsonUtility.FromJson<SimulationPayload>(requestBody);
                    responsePayload = sceneController.RunSimulation(simPayload);
                    break;
                // *** NEW: Query Endpoints ***
                case "get_object_position":
                    var queryPayload = JsonUtility.FromJson<QueryPayload>(requestBody);
                    responsePayload = sceneController.GetObjectPosition(queryPayload);
                    break;
                case "list_all_objects":
                     responsePayload = sceneController.ListAllObjects();
                     break;
                default:
                    responsePayload = new ApiResponse { success = false, message = "Invalid endpoint." };
                    break;
            }
            
            SendResponse(context, responsePayload);
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


//Standardized movement controller for the Agent Cube

using System;
using Unity.Barracuda;
using Unity.MLAgents;
using UnityEngine;

namespace MLAgents
{
    public class AgentCubeMovement : MonoBehaviour
    {

        //ONLY ALLOW SCRIPTED MOVEMENT VIA ML-AGENTS OR OTHER HEURISTIC SCRIPTS
        [Header("INPUT")]
        public bool allowHumanInputAndDisableAgentHeuristicInput = true;

        [Header("RIGIDBODY")] public float maxAngularVel = 50;
        [Header("RUNNING")] public ForceMode runningForceMode = ForceMode.Impulse;
        //speed agent can run if grounded
        public float agentRunSpeed = 10;
        public float agentTerminalVel = 20;
        //speed agent can run if not grounded
        public float agentRunInAirSpeed = 7f;

        [Header("DASH")]
        public float dashBoostForce = 20f;
        public ForceMode dashForceMode = ForceMode.Impulse;
        public bool dashPressed;
        public float dashCoolDownDuration = .2f;
        public float dashCoolDownTimer;

        [Header("IDLE")]
        //coefficient used to dampen velocity when idle
        //the purpose of this is to fine tune agent drag
        //...and prevent the agent sliding around while grounded
        //0 means it will instantly stop when grounded
        //1 means no drag will be applied
        public float agentIdleDragVelCoeff = .9f;

        public enum RotationAxes { MouseXAndY = 0, MouseX = 1, MouseY = 2 };

        [Header("BODY ROTATION")]
        public float MouseSensitivity = 1;
        // public float JoySensitivity = 100000f;
        public float mouseSmoothing = 0.5f;
        public float MouseSmoothTime = 0.05f;
        private float m_Yaw; // USED FOR AIMING WITH MOUSE
        private float m_SmoothYaw; // USED FOR AIMING WITH MOUSE
        private float m_YawSmoothV; // USED FOR AIMING WITH MOUSE
        Quaternion originalRotation;
        public float rotateSpeed = 100f; // Amount the player should turn while holding the turn button

        [Header("FALLING FORCE")]
        //force applied to agent while falling
        public float agentFallingSpeed = 50f;

        [Header("ANIMATE MESH")] public bool AnimateBodyMesh;
        public AnimationCurve walkingBounceCurve;
        public float walkingAnimScale = 1;
        public Transform bodyMesh;
        private float m_animateBodyMeshCurveTimer;

        private Rigidbody rb;
        public AgentCubeGroundCheck groundCheck;
        private float inputH;
        private float inputV;
        private const string ShootTethyx = "TethyxFire"; //Constant string for finding the trigger button on tethyx
        DodgeBallAgentInput m_Input;

        private DodgeBallAgent m_Agent;
        void Awake()
        {
            rb = GetComponent<Rigidbody>();
            groundCheck = GetComponent<AgentCubeGroundCheck>();
            m_Agent = GetComponent<DodgeBallAgent>();
            rb.maxAngularVelocity = maxAngularVel;
            originalRotation = transform.localRotation;
            var envParameters = Academy.Instance.EnvironmentParameters;
            m_Input = GetComponent<DodgeBallAgentInput>();
        }
        
        public static float ClampAngle(float angle, float min, float max)
        {
            if (angle < -360F)
                angle += 360F;
            if (angle > 360F)
                angle -= 360F;
            return Mathf.Clamp(angle, min, max);
        }
        
        // USED FOR ROTATION WITH Z AND X
        // public void LookZX() {
        //     float rotateAmount = 0f;
        //     if (Input.GetKey(KeyCode.Z)) {
        //         rotateAmount = -1f;
        //     } else if (Input.GetKey(KeyCode.X)) {
        //         rotateAmount = 1f;
        //     }
        //     transform.Rotate(Vector3.up, rotateAmount * rotateSpeed * Time.deltaTime);
        // }
        
        // USED FOR AIMING WITH MOUSE
        public void Look(float xRot = 0)
        {
            m_Yaw += xRot * MouseSensitivity;
            float smoothYawOld = m_SmoothYaw;
            m_SmoothYaw = Mathf.SmoothDampAngle(m_SmoothYaw, m_Yaw, ref m_YawSmoothV, MouseSmoothTime);
            rb.MoveRotation(rb.rotation * Quaternion.AngleAxis(Mathf.DeltaAngle(smoothYawOld, m_SmoothYaw), transform.up));
        }
        
        // USED FOR AIMING WITH THE TETHYX JOYSTICK
        public void LookT()
        {
            float tethyxInput = Input.GetAxis("TethyxHorizontal");
            
            tethyxInput *= 1.5f;
            //OUTCOMMENTED FOR TESTING, THESE ARE 7T EXCLUSIVE ADAPTIONS
            /*
            // Upper deazone + then compensating the speed to achieve same max rotational speed.
            tethyxInput = Mathf.Clamp(tethyxInput, -0.3f, 0.4f);
            if (tethyxInput <= 0)
            {
                tethyxInput *= 2.2f;
            }
            */
            
            m_Yaw += tethyxInput * 3;
            float smoothYawOld = m_SmoothYaw;
            m_SmoothYaw = Mathf.SmoothDampAngle(m_SmoothYaw, m_Yaw, ref m_YawSmoothV, MouseSmoothTime);
            rb.MoveRotation(rb.rotation * Quaternion.AngleAxis(Mathf.DeltaAngle(smoothYawOld, m_SmoothYaw), transform.up));
        }

        void FixedUpdate()
        {
            dashCoolDownTimer += Time.fixedDeltaTime;

            if (groundCheck && !groundCheck.isGrounded)
            {
                AddFallingForce(rb);
            }

            if (m_Agent)
            {
                //this disables the heuristic input collection
                m_Agent.disableInputCollectionInHeuristicCallback = allowHumanInputAndDisableAgentHeuristicInput;
            }
            if (!allowHumanInputAndDisableAgentHeuristicInput || m_Agent.Stunned)
            {
                return;
            }

            float rotate = 0;
            if (!ReferenceEquals(null, m_Input))
            {
                rotate = m_Input.rotateInput;
                
                /*
                 * Note:
                 * The Tethyx Trainer control doesnt reach the same speed as the button inputs does. It maxes out around
                 * 8, while the button inputs reach speeds of around 9.4. This feels a bit wonky and should probably be
                 * accounted for.
                 */
                
                // inputH = Input.GetAxis("TethyxHaorizontal"); //For movement with Tethyx Joystick
                inputV = Input.GetAxis("TethyxVertical"); //For movement with Tethyx Joystick
                
                inputH = m_Input.moveInput.x; // For movement with WASD
                // inputV = m_Input.moveInput.y; // For movement with WASD
            }
            var movDir = transform.TransformDirection(new Vector3(inputH, 0, inputV));
            RunOnGround(movDir);
            Look(rotate); // USED FOR AIMING WITH MOUSE
            LookT();
            // LookZX();

            if (m_Input.CheckIfInputSinceLastFrame(ref m_Input.m_dashPressed))
            {
                Dash(rb.transform.TransformDirection(new Vector3(inputH, 0, inputV)));
            }
            if ((m_Agent && m_Input.CheckIfInputSinceLastFrame(ref m_Input.m_throwPressed)) || Input.GetButtonDown(ShootTethyx))
            {
                m_Agent.ThrowTheBall();
            }
        }

        public void Dash(Vector3 dir)
        {
            if (dir != Vector3.zero && dashCoolDownTimer > dashCoolDownDuration)
            {
                rb.velocity = Vector3.zero;
                rb.AddForce(dir.normalized * dashBoostForce, dashForceMode);
                dashCoolDownTimer = 0;
            }
        }

        public void RotateTowards(Vector3 dir, float maxRotationRate = 1)
        {
            if (dir != Vector3.zero)
            {
                var rot = Quaternion.LookRotation(dir);
                var smoothedRot = Quaternion.RotateTowards(rb.rotation, rot, maxRotationRate * Time.deltaTime);
                rb.MoveRotation(smoothedRot);
            }
        }

        public void RunOnGround(Vector3 dir)
        {

            //ADD FORCE
            var vel = rb.velocity.magnitude;
            float adjustedSpeed = Mathf.Clamp(agentRunSpeed - vel, 0, agentTerminalVel);
            rb.AddForce(dir * adjustedSpeed, runningForceMode);

            //ANIMATE MESH
            if (dir == Vector3.zero)
            {
                if (AnimateBodyMesh)
                {
                    bodyMesh.localPosition = Vector3.zero;
                }
            }
            else
            {
                if (AnimateBodyMesh)
                {
                    bodyMesh.localPosition = Vector3.zero +
                                             Vector3.up * walkingAnimScale * walkingBounceCurve.Evaluate(
                                                 m_animateBodyMeshCurveTimer);
                    m_animateBodyMeshCurveTimer += Time.fixedDeltaTime;
                }
            }
        }

        public void RunInAir(Rigidbody rb, Vector3 dir)
        {
            var vel = rb.velocity.magnitude;
            float adjustedSpeed = Mathf.Clamp(agentRunInAirSpeed - vel, 0, agentTerminalVel);
            rb.AddForce(dir.normalized * adjustedSpeed,
                runningForceMode);
        }

        public void AddIdleDrag(Rigidbody rb)
        {
            rb.velocity *= agentIdleDragVelCoeff;
        }

        public void AddFallingForce(Rigidbody rb)
        {
            rb.AddForce(
                Vector3.down * agentFallingSpeed, ForceMode.Acceleration);
        }
    }
}

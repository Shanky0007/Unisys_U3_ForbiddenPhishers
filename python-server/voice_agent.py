"""
Career Path Simulator - Voice Agent
LiveKit voice assistant for real-time career counseling using Gemini Realtime
Supports both web-based and inbound telephony (SIP) connections
"""

from dotenv import load_dotenv
from livekit import agents, rtc, api
from livekit.agents import AgentServer, AgentSession, Agent, room_io, RunContext
from livekit.agents import function_tool
from livekit.plugins import google

# Load environment variables
load_dotenv(".env.local")


# Career counselor system instructions
CAREER_COUNSELOR_INSTRUCTIONS = """You are an expert career counselor and advisor for the Career Path Simulator platform.

Your role is to help users navigate their career decisions by providing:

1. **Career Guidance**: Help users understand different career paths, industries, and roles based on their background and interests.

2. **Skill Assessment**: Discuss the user's current skills and identify gaps they need to fill for their target career.

3. **Education Advice**: Provide guidance on courses, certifications, and educational paths that would benefit their career goals.

4. **Market Insights**: Share knowledge about industry trends, job market conditions, and in-demand skills.

5. **Timeline Planning**: Help users create realistic timelines for achieving their career milestones.

6. **Financial Guidance**: Discuss the financial aspects of career transitions, including education costs, expected salaries, and ROI.

7. **Risk Assessment**: Help users understand the risks and challenges associated with different career choices.

**For phone calls**:
- Be extra clear and concise since callers can't see visual aids
- Confirm important information by repeating it back
- Offer to transfer the call if they need a human specialist
- End the call gracefully when the conversation concludes

Conversation Style:
- Be warm, supportive, and encouraging while remaining realistic and honest
- Listen carefully to understand the user's unique situation and goals
- Ask clarifying questions to better understand their background and aspirations
- Provide actionable, specific advice rather than generic suggestions
- Use concrete examples and data points when possible
- Be concise but thorough in your responses
- Speak naturally as if having a real conversation, avoid reading like a textbook

You have access to the Career Path Simulator system which can run detailed career simulations. 
If the user wants to run a full simulation, guide them to use the platform's simulation feature.

Remember: You're here to empower users to make informed career decisions. Be their trusted advisor and champion their success!
"""


class CareerCounselor(Agent):
    """Voice AI agent that acts as a career counselor - handles both web and phone calls"""
    
    def __init__(self, ctx: agents.JobContext, is_phone_call: bool = False) -> None:
        self._ctx = ctx
        self._is_phone_call = is_phone_call
        super().__init__(
            instructions=CAREER_COUNSELOR_INSTRUCTIONS,
        )
    
    @function_tool()
    async def end_call(self, ctx: RunContext) -> str:
        """End the current call. Use this when the user wants to hang up or end the conversation."""
        try:
            lk_api = api.LiveKitAPI()
            await lk_api.room.delete_room(api.DeleteRoomRequest(room=self._ctx.room.name))
            await lk_api.aclose()
            return "Call ended successfully"
        except Exception as e:
            return f"Error ending call: {str(e)}"
    
    @function_tool()
    async def transfer_call(self, ctx: RunContext, phone_number: str) -> str:
        """Transfer the call to another phone number (only works for phone calls).
        
        Args:
            phone_number: The phone number to transfer to (e.g., '+1234567890')
        """
        if not self._is_phone_call:
            return "Call transfer is only available for phone calls, not web sessions."
        
        try:
            # Find the SIP participant
            sip_participant = None
            for participant in self._ctx.room.remote_participants.values():
                if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
                    sip_participant = participant
                    break
            
            if not sip_participant:
                return "No phone participant found to transfer."
            
            lk_api = api.LiveKitAPI()
            await lk_api.sip.transfer_sip_participant(
                api.TransferSIPParticipantRequest(
                    room_name=self._ctx.room.name,
                    participant_identity=sip_participant.identity,
                    transfer_to=phone_number,
                )
            )
            await lk_api.aclose()
            return f"Transferring call to {phone_number}"
        except Exception as e:
            return f"Error transferring call: {str(e)}"


# Create the agent server
server = AgentServer()


def is_sip_participant(room: rtc.Room) -> bool:
    """Check if there's a SIP participant in the room (phone call)"""
    for participant in room.remote_participants.values():
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            return True
    return False


def get_caller_phone(room: rtc.Room) -> str | None:
    """Get the caller's phone number if available"""
    for participant in room.remote_participants.values():
        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            return participant.attributes.get("sip.phoneNumber") or participant.attributes.get("sip.callID")
    return None


@server.rtc_session(agent_name="telephony_agent")
async def career_voice_agent(ctx: agents.JobContext):
    """Main entry point - handles both web and inbound phone calls
    
    Agent name 'telephony_agent' matches your LiveKit + Twilio dispatch rule.
    """
    
    # Connect to the room first
    await ctx.connect()
    
    # Wait for participant to connect
    await ctx.wait_for_participant()
    
    # Detect if this is a phone call or web connection
    is_phone_call = is_sip_participant(ctx.room)
    caller_phone = get_caller_phone(ctx.room) if is_phone_call else None
    
    # Create the agent
    agent = CareerCounselor(ctx=ctx, is_phone_call=is_phone_call)
    
    # Create the agent session with Gemini Realtime
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Fenrir",  # Available: Puck, Charon, Kore, Fenrir, Aoede
            temperature=0.8,
            instructions=CAREER_COUNSELOR_INSTRUCTIONS,
            language="en-US",
        ),
    )
    
    # Start the session
    await session.start(
        room=ctx.room,
        agent=agent,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(),
            
        ),
    )
    
    # Generate appropriate greeting based on connection type
    if is_phone_call:
        greeting = f"""Greet the caller warmly and introduce yourself as their career counselor from Career Path Simulator.
        This is a phone call so be brief and clear.
        {f'They are calling from {caller_phone}.' if caller_phone else ''}
        Ask what career questions they have. Keep it to 2 sentences."""
    else:
        greeting = """Greet the user warmly and introduce yourself as their career counselor.
        Ask them what career questions they have or what they'd like to explore today.
        Keep the greeting brief and inviting - just 2-3 sentences."""
    
    await session.generate_reply(instructions=greeting)


if __name__ == "__main__":
    agents.cli.run_app(server)

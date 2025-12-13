"""
Career Path Simulator - Voice Agent
LiveKit voice assistant for real-time career counseling using Gemini Realtime
Supports both web-based and inbound telephony (SIP) connections
"""

import json
from dotenv import load_dotenv
from livekit import agents, rtc, api
from livekit.agents import AgentServer, AgentSession, Agent, room_io, RunContext
from livekit.agents import function_tool
from livekit.plugins import google
from src.database import connect_to_mongodb, get_user_by_phone, get_user_by_id, get_career_roadmap_by_user_id

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
    
    def __init__(self, ctx: agents.JobContext, is_phone_call: bool = False, user_data: dict = None, career_roadmap: dict = None) -> None:
        self._ctx = ctx
        self._is_phone_call = is_phone_call
        self._user_data = user_data  # User info from users collection
        self._career_roadmap = career_roadmap  # Career roadmap from career_roadmaps collection
        
        # Build dynamic instructions based on user context
        instructions = self._build_instructions()
        
        super().__init__(
            instructions=instructions,
        )
    
    def _build_instructions(self) -> str:
        """Build personalized instructions based on career roadmap"""
        base_instructions = CAREER_COUNSELOR_INSTRUCTIONS
        
        if self._user_data and self._career_roadmap:
            # User is registered and has a career roadmap - add personalized context
            roadmap_context = self._format_career_roadmap_context()
            personalized_instructions = f"""{base_instructions}

**IMPORTANT - EXISTING USER WITH CAREER ROADMAP:**
This caller is a registered user who has already selected a career path and has a personalized roadmap. Here is their career plan:

{roadmap_context}

Use this information to provide highly personalized advice:
- Reference their chosen career path and milestones
- Help them track progress on their roadmap
- Discuss specific skills they need to develop
- Answer questions about their financial projections and ROI
- Address any risks or concerns from their assessment
- Help them stay on track with their timeline
- Provide motivation based on their success probability

Remember their name and be encouraging about their career journey!"""
            return personalized_instructions
        elif self._user_data:
            # User is registered but has no roadmap yet
            no_roadmap_instructions = f"""{base_instructions}

**IMPORTANT - REGISTERED USER WITHOUT ROADMAP:**
This caller is registered ({self._user_data.get('username', 'user')}) but hasn't created a career roadmap yet.

Your approach:
1. Welcome them by name warmly
2. Let them know they haven't yet created a career simulation
3. Encourage them to use our platform to:
   - Fill out their career profile
   - Get matched with 3 ideal career paths
   - Select one and get a personalized roadmap with timeline, financials, and risk assessment
4. In the meantime, help them with general career guidance
5. Ask about their career interests and goals

Be helpful and guide them toward creating their personalized career roadmap!"""
            return no_roadmap_instructions
        else:
            # New user - add instructions for gathering information
            new_user_instructions = f"""{base_instructions}

**IMPORTANT - NEW CALLER:**
This caller is not registered in our system. Their phone number was not found in our database.

Your approach for new callers:
1. Welcome them warmly and introduce yourself
2. Let them know they're not yet registered in our system
3. Ask for their name to address them personally
4. Understand their current situation (student, professional, career changer)
5. Ask about their educational background and career interests
6. Provide helpful guidance based on what they share
7. Encourage them to register on our platform for a full personalized career simulation

Be helpful even though they're new - gather information naturally during the conversation."""
            return new_user_instructions
    
    def _format_career_roadmap_context(self) -> str:
        """Format career roadmap data into readable context for the agent"""
        if not self._career_roadmap:
            return "No roadmap data available."
        
        roadmap = self._career_roadmap
        user = self._user_data or {}
        
        context_parts = []
        
        # User basic info
        if user.get("username"):
            context_parts.append(f"**Name:** {user.get('username')}")
        
        # Selected Career
        selected = roadmap.get("selected_career")
        if selected:
            context_parts.append(f"\n## SELECTED CAREER PATH")
            if selected.get("title"):
                context_parts.append(f"**Career Title:** {selected.get('title')}")
            if selected.get("field"):
                context_parts.append(f"**Field:** {selected.get('field')}")
            if selected.get("fit_score"):
                context_parts.append(f"**Fit Score:** {selected.get('fit_score')}%")
            if selected.get("tagline"):
                context_parts.append(f"**Tagline:** {selected.get('tagline')}")
            if selected.get("difficulty_level"):
                context_parts.append(f"**Difficulty:** {selected.get('difficulty_level')}")
            if selected.get("time_to_entry"):
                context_parts.append(f"**Time to Entry:** {selected.get('time_to_entry')}")
            if selected.get("typical_salary_range"):
                context_parts.append(f"**Salary Range:** {selected.get('typical_salary_range')}")
        
        # Summary
        summary = roadmap.get("summary")
        if summary:
            context_parts.append(f"\n## SUMMARY")
            if summary.get("success_probability"):
                context_parts.append(f"**Success Probability:** {summary.get('success_probability')}%")
            if summary.get("total_investment"):
                context_parts.append(f"**Total Investment:** ${summary.get('total_investment'):,}")
            if summary.get("break_even_year"):
                context_parts.append(f"**Break Even:** Year {summary.get('break_even_year')}")
        
        # Risk Assessment
        risk = roadmap.get("risk_assessment")
        if risk:
            context_parts.append(f"\n## RISK ASSESSMENT")
            if risk.get("success_probability_score"):
                context_parts.append(f"**Success Probability:** {risk.get('success_probability_score')}%")
            if risk.get("success_reasoning"):
                context_parts.append(f"**Analysis:** {risk.get('success_reasoning')[:300]}...")
            if risk.get("positive_factors"):
                factors = risk.get("positive_factors")[:3]
                context_parts.append(f"**Positive Factors:** {', '.join(factors)}")
            if risk.get("key_concerns"):
                concerns = risk.get("key_concerns")[:3]
                context_parts.append(f"**Key Concerns:** {', '.join(concerns)}")
            if risk.get("recommendations"):
                recs = risk.get("recommendations")[:3]
                context_parts.append(f"**Recommendations:** {'; '.join(recs)}")
        
        # Financial Analysis
        financial = roadmap.get("financial_analysis")
        if financial:
            context_parts.append(f"\n## FINANCIAL ANALYSIS")
            if financial.get("total_investment_required"):
                context_parts.append(f"**Total Investment Required:** ${financial.get('total_investment_required'):,.0f}")
            if financial.get("five_year_roi"):
                context_parts.append(f"**5-Year ROI:** {financial.get('five_year_roi')}%")
            if financial.get("break_even_year"):
                context_parts.append(f"**Break Even Year:** {financial.get('break_even_year')}")
            if financial.get("affordability_rating"):
                context_parts.append(f"**Affordability:** {financial.get('affordability_rating')}")
            if financial.get("meets_min_salary_target") is not None:
                context_parts.append(f"**Meets Salary Target:** {'Yes' if financial.get('meets_min_salary_target') else 'No'}")
            if financial.get("salary_milestones"):
                milestones = financial.get("salary_milestones")[:3]
                milestone_strs = [f"Year {m.get('year')}: ${m.get('expected_salary'):,}" for m in milestones if isinstance(m, dict)]
                if milestone_strs:
                    context_parts.append(f"**Salary Progression:** {' → '.join(milestone_strs)}")
        
        # Gap Analysis
        gap = roadmap.get("gap_analysis")
        if gap:
            context_parts.append(f"\n## SKILL GAPS TO ADDRESS")
            if gap.get("overall_gap_score"):
                context_parts.append(f"**Overall Gap Score:** {gap.get('overall_gap_score')}/100")
            if gap.get("gap_category"):
                context_parts.append(f"**Gap Category:** {gap.get('gap_category')}")
            if gap.get("technical_skill_gaps"):
                tech_gaps = gap.get("technical_skill_gaps")[:5]
                gap_names = [g.get("skill_name") for g in tech_gaps if isinstance(g, dict)]
                if gap_names:
                    context_parts.append(f"**Technical Skills to Develop:** {', '.join(gap_names)}")
            if gap.get("certification_gaps"):
                certs = gap.get("certification_gaps")[:3]
                context_parts.append(f"**Certifications Needed:** {', '.join(certs)}")
            if gap.get("top_priorities"):
                priorities = gap.get("top_priorities")[:3]
                context_parts.append(f"**Top Priorities:** {'; '.join(priorities)}")
        
        # Timeline highlights
        timeline = roadmap.get("timeline")
        if timeline:
            context_parts.append(f"\n## CAREER TIMELINE")
            if isinstance(timeline, dict):
                if timeline.get("recommended_path"):
                    context_parts.append(f"**Recommended Path:** {timeline.get('recommended_path')}")
                # Get year plans if available
                for path_type in ["realistic_path", "conservative_path", "ambitious_path"]:
                    path = timeline.get(path_type)
                    if path and isinstance(path, dict):
                        if path.get("total_years"):
                            context_parts.append(f"**Total Years:** {path.get('total_years')}")
                        if path.get("final_target_role"):
                            context_parts.append(f"**Target Role:** {path.get('final_target_role')}")
                        if path.get("major_milestones"):
                            milestones = path.get("major_milestones")[:4]
                            context_parts.append(f"**Key Milestones:** {'; '.join(milestones)}")
                        break
        
        return "\n".join(context_parts) if context_parts else "Limited roadmap data available."
    
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


def get_user_id_from_participant(participant: rtc.Participant) -> str | None:
    """
    Extract user_id from participant metadata or attributes.
    The frontend should pass the user_id when creating the LiveKit access token.
    
    The user_id can be passed in:
    1. participant.metadata - as JSON string with 'user_id' field
    2. participant.attributes - as 'user_id' attribute
    3. participant.identity - if it's set to the user_id on the frontend
    
    Returns:
        The user_id string or None if not found
    """
    user_id = None
    
    # Try to get from attributes first (recommended approach)
    if participant.attributes:
        user_id = participant.attributes.get("user_id") or participant.attributes.get("userId")
        if user_id:
            print(f"✅ Found user_id in participant attributes: {user_id}")
            return user_id
    
    # Try to get from metadata (JSON string)
    if participant.metadata:
        try:
            metadata = json.loads(participant.metadata)
            user_id = metadata.get("user_id") or metadata.get("userId")
            if user_id:
                print(f"✅ Found user_id in participant metadata: {user_id}")
                return user_id
        except json.JSONDecodeError:
            # Metadata might be a plain string (user_id itself)
            if participant.metadata and len(participant.metadata) == 24:  # MongoDB ObjectId length
                print(f"✅ Treating participant metadata as user_id: {participant.metadata}")
                return participant.metadata
    
    # Fallback: use participant identity if it looks like a MongoDB ObjectId
    if participant.identity and len(participant.identity) == 24:
        print(f"ℹ️ Using participant identity as potential user_id: {participant.identity}")
        return participant.identity
    
    print(f"⚠️ No user_id found in participant data. Identity: {participant.identity}, Metadata: {participant.metadata}, Attributes: {participant.attributes}")
    return None


@server.rtc_session(agent_name="telephony_agent")
async def career_voice_agent(ctx: agents.JobContext):
    """Main entry point - handles both web and inbound phone calls
    
    Agent name 'telephony_agent' matches your LiveKit + Twilio dispatch rule.
    
    For web connections:
    - The frontend should pass user_id in participant attributes or metadata when creating the access token
    - Example token creation on frontend:
        token.addGrant({ roomJoin: true, room: roomName })
        token.metadata = JSON.stringify({ user_id: "user_id_here" })
        OR
        token.attributes = { user_id: "user_id_here" }
    
    For phone calls:
    - User is identified by their phone number from the SIP participant
    """
    
    # Connect to MongoDB for user verification
    await connect_to_mongodb()
    
    # Connect to the room first
    await ctx.connect()
    
    # Wait for participant to connect
    participant = await ctx.wait_for_participant()
    
    # Detect if this is a phone call or web connection
    is_phone_call = is_sip_participant(ctx.room)
    caller_phone = get_caller_phone(ctx.room) if is_phone_call else None
    
    # Initialize user data variables
    user_data = None
    career_roadmap = None
    is_registered_user = False
    
    if is_phone_call and caller_phone:
        # For phone calls, verify the caller against the database by phone number
        print(f"📞 Incoming call from: {caller_phone}")
        
        # Look up the user by phone number
        user_data = await get_user_by_phone(caller_phone)
        
        if user_data:
            print(f"✅ Found registered user: {user_data.get('username', 'Unknown')}")
            is_registered_user = True
            
            # Fetch user's career roadmap using their user_id
            user_id = user_data.get("_id")
            if user_id:
                career_roadmap = await get_career_roadmap_by_user_id(user_id)
                if career_roadmap:
                    selected_career = career_roadmap.get("selected_career", {})
                    print(f"✅ Found career roadmap for: {user_data.get('username')} - Career: {selected_career.get('title', 'Unknown')}")
                else:
                    print(f"⚠️ User {user_data.get('username')} has no career roadmap yet")
        else:
            print(f"❌ Phone number {caller_phone} not found in database - new caller")
    else:
        # For web connections, get user_id from participant metadata/attributes
        print(f"🌐 Web connection from participant: {participant.identity}")
        
        user_id = get_user_id_from_participant(participant)
        
        if user_id:
            print(f"🔍 Looking up user by ID: {user_id}")
            
            # Get user data from database
            user_data = await get_user_by_id(user_id)
            
            if user_data:
                print(f"✅ Found web user: {user_data.get('username', 'Unknown')}")
                is_registered_user = True
                
                # Fetch user's career roadmap
                career_roadmap = await get_career_roadmap_by_user_id(user_id)
                if career_roadmap:
                    selected_career = career_roadmap.get("selected_career", {})
                    print(f"✅ Found career roadmap for web user: {user_data.get('username')} - Career: {selected_career.get('title', 'Unknown')}")
                else:
                    print(f"⚠️ Web user {user_data.get('username')} has no career roadmap yet")
            else:
                print(f"❌ User ID {user_id} not found in database")
        else:
            print(f"⚠️ No user_id provided for web connection - treating as anonymous user")
    
    # Create the agent with user context
    agent = CareerCounselor(
        ctx=ctx, 
        is_phone_call=is_phone_call,
        user_data=user_data,
        career_roadmap=career_roadmap
    )
    
    # Create the agent session with Gemini Realtime
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Fenrir",  # Available: Puck, Charon, Kore, Fenrir, Aoede
            temperature=0.8,
            instructions=agent._build_instructions(),  # Use the personalized instructions
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
    
    # Generate appropriate greeting based on connection type and user status
    if is_phone_call:
        if is_registered_user and user_data and career_roadmap:
            username = user_data.get("username", "there")
            selected_career = career_roadmap.get("selected_career", {})
            career_title = selected_career.get("title", "your chosen career")
            greeting = f"""Greet {username} by name warmly! You recognize them as a returning user with a career roadmap.
            This is a phone call so be brief and clear.
            Acknowledge that you remember their career path towards {career_title}.
            Ask how their journey is going or if they have specific questions about their roadmap.
            Keep it to 2-3 sentences and be warm and encouraging."""
        elif is_registered_user and user_data:
            username = user_data.get("username", "there")
            greeting = f"""Greet {username} by name warmly! You recognize them as a registered user.
            This is a phone call so be brief and clear.
            Let them know they haven't created a career roadmap yet.
            Encourage them to use our platform to get a personalized career simulation.
            Ask what career questions they have today. Keep it to 2-3 sentences."""
        else:
            greeting = f"""Greet the caller warmly and introduce yourself as their career counselor from Career Path Simulator.
            This is a phone call from an unregistered number so be brief and clear.
            Let them know you'd love to help with their career questions.
            Mention that for a personalized experience, they can register on our platform.
            Ask what career questions they have. Keep it to 2-3 sentences."""
    else:
        # Web connection greetings
        if is_registered_user and user_data and career_roadmap:
            username = user_data.get("username", "there")
            selected_career = career_roadmap.get("selected_career", {})
            career_title = selected_career.get("title", "your chosen career")
            greeting = f"""Greet {username} by name warmly! You recognize them as a returning user with a career roadmap.
            Acknowledge that you remember their career path towards {career_title}.
            Ask how their journey is going or if they have specific questions about their roadmap.
            Keep it to 2-3 sentences and be warm and encouraging."""
        elif is_registered_user and user_data:
            username = user_data.get("username", "there")
            greeting = f"""Greet {username} by name warmly! You recognize them as a registered user.
            Let them know they haven't created a career roadmap yet on our platform.
            Encourage them to complete a career simulation to get a personalized roadmap.
            Ask what career questions they have today. Keep it to 2-3 sentences."""
        else:
            greeting = """Greet the user warmly and introduce yourself as their career counselor from Career Path Simulator.
            Since they're not logged in, offer to help with general career questions.
            Mention that for a personalized experience with a tailored career roadmap, they can register on our platform.
            Ask them what career questions they have or what they'd like to explore today.
            Keep the greeting brief and inviting - just 2-3 sentences."""
    
    await session.generate_reply(instructions=greeting)


if __name__ == "__main__":
    agents.cli.run_app(server)

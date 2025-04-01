# PeopleAgent Version Details

This document summarizes the evolution of PeopleAgent, outlining each version's key features and overall improvements. The table below provides a quick overview for easy reference.

<table style="width:60%; border-collapse: collapse;">
  <colgroup>
    <col style="width:10%;">
    <col style="width:30%;">
    <col style="width:60%;">
  </colgroup>
  <thead>
    <tr>
      <th style="border: 1px solid #ddd; padding: 8px;">PeopleAgent Version</th>
      <th style="border: 1px solid #ddd; padding: 8px;">Summary</th>
      <th style="border: 1px solid #ddd; padding: 8px;">Key Features used</th>
    </tr>
  </thead>
  <tbody>
    <!-- v1 row -->
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;">v1</td>
      <td style="border: 1px solid #ddd; padding: 8px;">
        Generic implementation for PeopleAgent version 1 with basic capabilities.
      </td>
      <td style="border: 1px solid #ddd; padding: 8px;">
        <span style="color:green;">✔</span> Implements client credentials flow to authenticate with Microsoft Graph API<br>
        <span style="color:green;">✔</span> Fetches comprehensive user details including profiles, roles, and relationships<br>
        <span style="color:green;">✔</span> Processes natural language questions through Azure OpenAI<br>       
        <span style="color:green;">✔</span> Maintains conversation history for contextual understanding<br>
        <span style="color:green;">✔</span> Formats responses in a user-friendly, conversational manner<br>
        <span style="color:green;">✔</span> Handles various query types (find user, report structure, device information, etc.)
      </td>
    </tr>
    <!-- v2 row -->
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;">v2</td>
      <td style="border: 1px solid #ddd; padding: 8px;">
        The v2 implementation features a modular architecture that separates concerns for better maintainability, improved error handling, and enhanced performance when processing user queries about Microsoft 365 users.
      </td>
      <td style="border: 1px solid #ddd; padding: 8px;">
        <span style="color:green;">✔</span> Module based code<br>
        <span style="color:green;">✔</span> Improved context management for more natural conversations<br>
        <span style="color:green;">✔</span> Better error handling and logging capabilities<br>       
        <span style="color:green;">✔</span> Optimized API usage to reduce latency and token consumption<br>
       </td>
    </tr>
    <!-- v3 row -->
    <tr>
      <td style="border: 1px solid #ddd; padding: 8px;">v3</td>
      <td style="border: 1px solid #ddd; padding: 8px;">
        This version introduces advanced memory management and streaming capabilities to maintain conversation context and deliver real-time responses. It builds on previous implementations by integrating persistent storage, context sharing, and enhanced logging to optimize conversational interactions.
      </td>
      <td style="border: 1px solid #ddd; padding: 8px;">
        <span style="color:green;">✔</span> people_agent.py now maintains a conversation history and offers a clear_memory() method.<br>
        <span style="color:green;">✔</span> response_generation.py appends both the user query and agent response to history.<br>
        <span style="color:green;">✔</span> UI_v1_1_memory_streaming.py caches PeopleAgent instances per user and clears memory when sessions end or users switch.<br>
        <span style="color:green;">✔</span> people_agent.py now supports streaming responses via process_query, yielding response chunks.<br>
        <span style="color:green;">✔</span> response_generation.py includes a generator function to yield updated responses.<br>
        <span style="color:green;">✔</span> UI_v1_1_memory_streaming.py iterates over the streaming generator, logs each chunk with timing details, and updates the UI in real time.<br>
        
  
  </tbody>
</table>

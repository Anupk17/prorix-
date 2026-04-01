const API_KEY = process.env.EXPO_PUBLIC_GEMINI_API_KEY;
const BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent";

/**
 * Summarizes a massive feed of notifications from multiple apps into a unified bulleted list.
 */
export const summarizeAllNotifications = async (notifications: {app_name: string, message: string}[]): Promise<string> => {
  if (!notifications || notifications.length === 0) return "No notifications to summarize.";
  if (!API_KEY) {
    console.error("EXPO_PUBLIC_GEMINI_API_KEY is missing from environment variables.");
    return "API Key is missing. Please check your .env file.";
  }

  const formattedNotifs = notifications.map(n => `[${n.app_name}] ${n.message}`).join("\n");
  
  const prompt = `Summarize these recent alerts concisely using bullet points. Focus on key actions and important info only.
  
  Alerts:
  ${formattedNotifs}
  
  Brief Summary:`;

  try {
    const response = await fetch(`${BASE_URL}?key=${API_KEY}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [{ text: prompt }]
        }],
        generationConfig: {
          temperature: 0.4,
          topK: 1,
          topP: 1,
          maxOutputTokens: 250,
        }
      })
    });

    const data = await response.json();

    if (data.error) {
      throw new Error(data.error.message);
    }

    if (!data.candidates || data.candidates.length === 0 || !data.candidates[0].content) {
      return "The AI couldn't generate a summary at this time.";
    }

    return data.candidates[0].content.parts[0].text.trim();
  } catch (error: any) {
    console.error("Gemini Global Error:", error);
    return `Summary unavailable: ${error.message || "Unknown error"}`;
  }
};

/**
 * Summarizes notifications for a specific app.
 */
export const summarizeNotifications = async (notifications: string[], appName: string): Promise<string> => {
  if (!notifications || notifications.length === 0) return `No ${appName} notifications to summarize.`;
  if (!API_KEY) {
    console.error("EXPO_PUBLIC_GEMINI_API_KEY is missing from environment variables.");
    return "API Key is missing.";
  }

  const prompt = `Summarize these alerts for ${appName}:
  
  Alerts:
  ${notifications.join("\n")}
  
  Summary:`;

  try {
    const response = await fetch(`${BASE_URL}?key=${API_KEY}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        contents: [{
          parts: [{ text: prompt }]
        }],
        generationConfig: {
          temperature: 0.4,
          maxOutputTokens: 150,
        }
      })
    });

    const data = await response.json();

    if (data.error) {
      throw new Error(data.error.message);
    }

    if (!data.candidates || data.candidates.length === 0 || !data.candidates[0].content) {
      return "Could not generate summary for this app.";
    }

    return data.candidates[0].content.parts[0].text.trim();
  } catch (error: any) {
    console.error("Gemini Individual App Error:", error);
    return `Error: ${error.message || "Failed to fetch summary"}`;
  }
};

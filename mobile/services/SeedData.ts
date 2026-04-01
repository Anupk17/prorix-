import { saveNotification, getApps, getDb } from './database';

export const seedMockNotifications = async () => {
  const apps = await getApps();
  const mockMessages: Record<string, string[]> = {
    "WhatsApp": ["Dinner at 8?", "Can you send the docs?", "See you tomorrow!"],
    "GPay": ["Payment of ₹500 successful", "Cashback earned!", "Check your balance"],
    "Zomato": ["Order on the way!", "Rate your last meal", "40% off on your next order"],
    "Instagram": ["New follower: john_doe", "Liked your story", "Check out this reel"],
    "Zepto": ["Delivered in 10 mins!", "Fresh mangoes available", "Order #1234 packed"],
  };

  for (const app of apps) {
    // Check if notifications already exist for this app
    const count = await getDb().getFirstAsync<{count: number}>(
      'SELECT COUNT(*) as count FROM Notifications WHERE app_id = ?', [app.app_id]
    );

    if (count?.count === 0) {
      const messages = mockMessages[app.app_name] || ["Notification from " + app.app_name];
      for (const msg of messages) {
        await saveNotification(app.app_id, msg);
      }
    }
  }
};

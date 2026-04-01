import React, { useEffect, useState } from 'react';
import { StyleSheet, FlatList, TouchableOpacity, View, Text, Modal, Alert, Pressable, Switch, TextInput } from 'react-native';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { initDb, getNotifications, markRead, markDismissed, updateBanditWeight, updateUser } from '@/services/database';
import { seedMockNotifications } from '@/services/SeedData';
import { summarizeNotifications, summarizeAllNotifications } from '@/services/gemini';
import { useRouter } from 'expo-router';
import * as DocumentPicker from 'expo-document-picker';

export default function HomeScreen() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [filteredNotifications, setFilteredNotifications] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [profileVisible, setProfileVisible] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [userName, setUserName] = useState('Demo User');
  const [userEmail, setUserEmail] = useState('demo@priorix.com');
  const [menuVisible, setMenuVisible] = useState(false);
  const [soundPriority, setSoundPriority] = useState(true);
  const [reduceVolume, setReduceVolume] = useState(false);
  const router = useRouter();

  const handleUpdateProfile = async () => {
    try {
      // For now using mock user ID 1
      await updateUser(1, userName, userEmail);
      setEditMode(false);
      Alert.alert("Success", "Profile updated successfully!");
    } catch (e) {
      Alert.alert("Error", "Failed to update profile.");
    }
  };

  const handlePickSound = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'audio/*',
        copyToCacheDirectory: true,
      });

      if (result.assets && result.assets.length > 0) {
        Alert.alert("Sound Selected", `Custom sound "${result.assets[0].name}" has been uploaded for prioritized apps.`);
      }
    } catch (e) {
      Alert.alert("Error", "Could not pick sound file.");
    }
  };

  const loadData = async () => {
    setRefreshing(true);
    const data = await getNotifications();
    if (data.length === 0) {
      await seedMockNotifications();
      const freshData = await getNotifications();
      setNotifications(freshData);
      setFilteredNotifications(freshData);
    } else {
      setNotifications(data);
      setFilteredNotifications(data);
    }
    setRefreshing(false);
  };

  useEffect(() => {
    const results = notifications.filter(notif =>
      notif.app_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      notif.message.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredNotifications(results);
  }, [searchQuery, notifications]);

  useEffect(() => {
    loadData();
  }, []);

  const handleAction = async (id: number, appId: number, action: 'read' | 'dismiss') => {
    if (action === 'read') {
      await markRead(id, appId);
      await updateBanditWeight(appId, 1.0);
    } else {
      await markDismissed(id, appId);
      await updateBanditWeight(appId, -0.3);
    }
    loadData();
  };

  const handleSummarize = async (appId: number, name: string) => {
    const appNotifs = notifications.filter(n => n.app_id === appId).map(n => n.message);
    if (appNotifs.length < 2) {
      Alert.alert("Info", `Need at least 2 notifications from ${name} for a summary.`);
      return;
    }
    
    try {
      setRefreshing(true); // Show loading while summarizing
      const summary = await summarizeNotifications(appNotifs, name);
      setRefreshing(false);
      Alert.alert(
        `AI Summary: ${name}`,
        summary,
        [{ text: "Great!", style: "default" }]
      );
    } catch (e) {
      setRefreshing(false);
      Alert.alert("Error", "Could not generate summary. Check your Gemini API Key in services/gemini.ts.");
    }
  };

  const handleSummarizeAll = async () => {
    if (notifications.length === 0) {
      Alert.alert("Info", "No notifications to summarize.");
      return;
    }
    
    try {
      setRefreshing(true);
      const summary = await summarizeAllNotifications(notifications.map(n => ({
        app_name: n.app_name,
        message: n.message
      })));
      setRefreshing(false);
      Alert.alert(
        "AI Intelligence: All Notifications",
        summary,
        [{ text: "Done", style: "cancel" }]
      );
    } catch (e) {
      setRefreshing(false);
      Alert.alert("Error", "Failed to summarize all notifications. Check API key.");
    }
  };

  const handleLogout = () => {
    setProfileVisible(false);
    router.replace('/login');
  };

  const renderItem = ({ item }: { item: any }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <View style={styles.appBadge}>
          <Text style={styles.appEmoji}>{item.app_emoji || '🔔'}</Text>
          <Text style={styles.appName}>{item.app_name}</Text>
        </View>
        <TouchableOpacity 
          style={styles.magicBtn}
          onPress={() => handleSummarize(item.app_id, item.app_name)}
        >
           <FontAwesome name="magic" size={16} color="#fff" />
           <Text style={styles.magicText}>AI Summary</Text>
        </TouchableOpacity>
      </View>
      <View style={styles.content}>
        <Text style={styles.message}>{item.message}</Text>
        <Text style={styles.time}>{new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Text>
      </View>
      <View style={styles.actions}>
        <TouchableOpacity style={[styles.btn, styles.btnDismiss]} onPress={() => handleAction(item.notif_id, item.app_id, 'dismiss')}>
          <FontAwesome name="times" size={16} color="#ef4444" />
          <Text style={[styles.btnText, { color: '#ef4444' }]}>Dismiss</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.btn, styles.btnRead]} onPress={() => handleAction(item.notif_id, item.app_id, 'read')}>
          <FontAwesome name="check" size={16} color="#22c55e" />
          <Text style={[styles.btnText, { color: '#22c55e' }]}>Read</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.topBar}>
        <TouchableOpacity style={styles.menuBtn} onPress={() => setMenuVisible(true)}>
          <FontAwesome name="bars" size={20} color="#cbd5e1" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>SMART notification</Text>
        <TouchableOpacity style={styles.userBtn} onPress={() => setProfileVisible(true)}>
          <View style={styles.userCircle} />
        </TouchableOpacity>
      </View>

      <Modal
        animationType="fade"
        transparent={true}
        visible={menuVisible}
        onRequestClose={() => setMenuVisible(false)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setMenuVisible(false)}>
          <View style={[styles.modalContent, styles.sideMenuContent]}>
             <View style={styles.menuHeader}>
               <Text style={styles.menuTitle}>Features</Text>
               <TouchableOpacity onPress={() => setMenuVisible(false)}>
                 <FontAwesome name="times" size={20} color="#64748b" />
               </TouchableOpacity>
             </View>

             <View style={styles.menuItem}>
               <View style={styles.menuItemInfo}>
                 <FontAwesome name="volume-up" size={18} color="#a78bfa" style={{ width: 25 }} />
                 <Text style={styles.menuItemText}>Sound Prioritization</Text>
               </View>
               <Switch 
                 value={soundPriority} 
                 onValueChange={setSoundPriority}
                 trackColor={{ false: "#334155", true: "#7c3aed" }}
               />
             </View>
             <Text style={styles.menuItemSubtext}>Set unique notification sounds based on app priority rank.</Text>

             <TouchableOpacity style={styles.uploadSoundBtn} onPress={handlePickSound}>
                <FontAwesome name="upload" size={14} color="#a78bfa" />
                <Text style={styles.uploadSoundText}>Select Custom Sound</Text>
             </TouchableOpacity>

             <View style={[styles.menuItem, { marginTop: 20 }]}>
               <View style={styles.menuItemInfo}>
                 <FontAwesome name="compress" size={18} color="#a78bfa" style={{ width: 25 }} />
                 <Text style={styles.menuItemText}>Reduce Noise</Text>
               </View>
               <Switch 
                 value={reduceVolume} 
                 onValueChange={setReduceVolume}
                 trackColor={{ false: "#334155", true: "#7c3aed" }}
               />
             </View>
             <Text style={styles.menuItemSubtext}>Automatically lower notification volume when receiving many messages at once.</Text>

             <TouchableOpacity style={[styles.modalOption, { marginTop: 30 }]} onPress={() => { setMenuVisible(false); router.push('/(tabs)/apps'); }}>
                <FontAwesome name="tasks" size={18} color="#cbd5e1" />
                <Text style={styles.modalOptionText}>Change Priority</Text>
             </TouchableOpacity>
             <TouchableOpacity style={styles.modalOption} onPress={() => { setMenuVisible(false); router.push('/(tabs)/two'); }}>
                <FontAwesome name="bar-chart" size={18} color="#cbd5e1" />
                <Text style={styles.modalOptionText}>Dashboard</Text>
             </TouchableOpacity>
          </View>
        </Pressable>
      </Modal>

      <Modal
        animationType="slide"
        transparent={true}
        visible={profileVisible}
        onRequestClose={() => setProfileVisible(false)}
      >
        <Pressable style={styles.modalOverlay} onPress={() => setProfileVisible(false)}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
               <View style={styles.modalUserCircle} />
               {editMode ? (
                 <View style={styles.editForm}>
                    <TextInput 
                      style={styles.modalInput} 
                      value={userName} 
                      onChangeText={setUserName}
                      placeholder="Name"
                      placeholderTextColor="#64748b"
                    />
                    <TextInput 
                      style={styles.modalInput} 
                      value={userEmail} 
                      onChangeText={setUserEmail}
                      placeholder="Email"
                      placeholderTextColor="#64748b"
                    />
                    <TouchableOpacity style={styles.saveBtn} onPress={handleUpdateProfile}>
                       <Text style={styles.saveBtnText}>Save Changes</Text>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => setEditMode(false)}>
                       <Text style={styles.cancelText}>Cancel</Text>
                    </TouchableOpacity>
                 </View>
               ) : (
                 <>
                    <Text style={styles.modalUserName}>{userName}</Text>
                    <Text style={styles.modalUserEmail}>{userEmail}</Text>
                 </>
               )}
             </View>
             
             <View style={styles.modalBody}>
               <TouchableOpacity style={styles.modalOption} onPress={() => setEditMode(!editMode)}>
                 <FontAwesome name="user" size={18} color="#94a3b8" />
                 <Text style={styles.modalOptionText}>Account Settings</Text>
               </TouchableOpacity>
               <TouchableOpacity style={styles.modalOption} onPress={() => Alert.alert("Logs", "Fetching recent notification logs...")}>
                 <FontAwesome name="bell" size={18} color="#94a3b8" />
                 <Text style={styles.modalOptionText}>Notification Logs</Text>
               </TouchableOpacity>
              <TouchableOpacity style={styles.modalOption} onPress={handleLogout}>
                <FontAwesome name="sign-out" size={18} color="#ef4444" />
                <Text style={[styles.modalOptionText, { color: '#ef4444' }]}>Logout</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Pressable>
      </Modal>

      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Priority Feed</Text>
          <Text style={styles.subtitle}>AI-sorted by your habits</Text>
        </View>
        <View style={styles.headerActions}>
          <TouchableOpacity style={styles.summarizeAllBtn} onPress={handleSummarizeAll}>
             <FontAwesome name="bolt" size={18} color="#fff" />
             <Text style={styles.summarizeAllText}>Summarize All</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.refreshBtn} onPress={loadData}>
            <FontAwesome name="refresh" size={18} color="#a78bfa" />
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.searchBar}>
        <FontAwesome name="search" size={16} color="#64748b" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search apps or messages..."
          placeholderTextColor="#64748b"
          value={searchQuery}
          onChangeText={setSearchQuery}
          clearButtonMode="while-editing"
        />
      </View>
      <FlatList
        data={filteredNotifications}
        renderItem={renderItem}
        keyExtractor={(item) => item.notif_id.toString()}
        contentContainerStyle={styles.list}
        onRefresh={loadData}
        refreshing={refreshing}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyEmoji}>🎉</Text>
            <Text style={styles.empty}>All caught up!</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f1a', paddingTop: 20 },
  topBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    height: 60,
  },
  menuBtn: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 16,
    color: '#cbd5e1',
    fontWeight: '600',
    letterSpacing: 0.5,
  },
  userBtn: {
    padding: 5,
  },
  userCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    borderWidth: 1.5,
    borderColor: '#ef4444', // Red circle from sketch
    backgroundColor: 'rgba(255,255,255,0.05)',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#1a1a2e',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    minHeight: 350,
  },
  sideMenuContent: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    width: '80%',
    borderTopRightRadius: 24,
    borderBottomRightRadius: 24,
    borderTopLeftRadius: 0,
  },
  menuHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 30,
    marginTop: 20,
  },
  menuTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#f8fafc',
  },
  menuItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  menuItemInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  menuItemText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#e2e8f0',
  },
  menuItemSubtext: {
    fontSize: 12,
    color: '#64748b',
    marginTop: 5,
    paddingRight: 40,
  },
  modalHeader: {
    alignItems: 'center',
    marginBottom: 30,
  },
  modalUserCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#334155',
    borderWidth: 2,
    borderColor: '#ef4444',
    marginBottom: 15,
  },
  modalUserName: {
    fontSize: 20,
    fontWeight: '800',
    color: '#f8fafc',
  },
  modalUserEmail: {
    fontSize: 14,
    color: '#94a3b8',
    marginTop: 4,
  },
  editForm: {
    width: '100%',
    alignItems: 'center',
    gap: 10,
  },
  modalInput: {
    width: '100%',
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 12,
    padding: 12,
    color: '#f8fafc',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  saveBtn: {
    backgroundColor: '#7c3aed',
    paddingVertical: 10,
    paddingHorizontal: 30,
    borderRadius: 10,
    marginTop: 10,
  },
  saveBtnText: {
    color: 'white',
    fontWeight: '700',
  },
  cancelText: {
    color: '#64748b',
    marginTop: 5,
    fontSize: 12,
  },
  uploadSoundBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(124,58,237,0.1)',
    padding: 10,
    borderRadius: 8,
    marginTop: 10,
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderColor: 'rgba(124,58,237,0.2)',
  },
  uploadSoundText: {
    color: '#a78bfa',
    fontSize: 12,
    fontWeight: '700',
    marginLeft: 8,
  },
  modalBody: {
    gap: 15,
  },
  modalOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  modalOptionText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#cbd5e1',
    marginLeft: 15,
  },
  header: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    paddingHorizontal: 20, 
    marginVertical: 15 
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.05)',
    marginHorizontal: 20,
    paddingHorizontal: 15,
    borderRadius: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.08)',
  },
  searchIcon: {
    marginRight: 10,
  },
  searchInput: {
    flex: 1,
    height: 45,
    color: '#e2e8f0',
    fontSize: 14,
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  summarizeAllBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#7c3aed',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 12,
    shadowColor: '#7c3aed',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  summarizeAllText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 12,
    marginLeft: 6,
  },
  title: { fontSize: 28, fontWeight: '800', color: '#e2e8f0' },
  subtitle: { fontSize: 14, color: '#64748b' },
  refreshBtn: { 
    padding: 10, 
    backgroundColor: 'rgba(124,58,237,0.1)', 
    borderRadius: 12 
  },
  list: { padding: 15 },
  card: { 
    backgroundColor: 'rgba(255,255,255,0.03)', 
    borderRadius: 20, 
    marginBottom: 15, 
    padding: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  cardHeader: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    marginBottom: 12 
  },
  appBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.05)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  appEmoji: { fontSize: 16, marginRight: 6 },
  appName: { fontSize: 14, fontWeight: '700', color: '#cbd5e1' },
  magicBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#7c3aed',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 10,
  },
  magicText: { color: 'white', fontSize: 11, fontWeight: '700', marginLeft: 5 },
  content: { marginBottom: 15 },
  message: { fontSize: 16, color: '#f1f5f9', lineHeight: 22, fontWeight: '500' },
  time: { fontSize: 12, color: '#475569', marginTop: 8 },
  actions: { 
    flexDirection: 'row', 
    justifyContent: 'flex-end',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.05)',
    paddingTop: 12,
  },
  btn: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    paddingHorizontal: 12, 
    paddingVertical: 6,
    borderRadius: 8,
    marginLeft: 10,
  },
  btnDismiss: { backgroundColor: 'rgba(239, 68, 68, 0.1)' },
  btnRead: { backgroundColor: 'rgba(34, 197, 94, 0.1)' },
  btnText: { fontSize: 13, fontWeight: '700', marginLeft: 6 },
  emptyContainer: { alignItems: 'center', marginTop: 100 },
  emptyEmoji: { fontSize: 40, marginBottom: 10 },
  empty: { fontSize: 16, color: '#64748b', fontWeight: '600' },
});

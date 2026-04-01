import React, { useEffect, useState } from 'react';
import { StyleSheet, FlatList, TouchableOpacity, View, Text, Switch, Alert } from 'react-native';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { getAppsWithPriority, updateAppStatus, updatePriorityOrder } from '@/services/database';

export default function AppsScreen() {
  const [apps, setApps] = useState<any[]>([]);

  const loadApps = async () => {
    const data = await getAppsWithPriority();
    setApps(data);
  };

  useEffect(() => {
    loadApps();
  }, []);

  const toggleApp = async (appId: number, currentStatus: number) => {
    const newStatus = currentStatus === 1 ? false : true;
    await updateAppStatus(appId, newStatus);
    loadApps();
  };

  const movePriority = async (index: number, direction: 'up' | 'down') => {
    if (direction === 'up' && index === 0) return;
    if (direction === 'down' && index === apps.length - 1) return;

    const newApps = [...apps];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    
    // Swap in local state for immediate UI feedback
    [newApps[index], newApps[targetIndex]] = [newApps[targetIndex], newApps[index]];
    setApps(newApps);

    // Persist to DB
    await updatePriorityOrder(newApps[index].app_id, index + 1);
    await updatePriorityOrder(newApps[targetIndex].app_id, targetIndex + 1);
    loadApps();
  };

  const renderItem = ({ item, index }: { item: any, index: number }) => (
    <View style={styles.appCard}>
      <View style={styles.appInfo}>
        <Text style={styles.emoji}>{item.app_emoji}</Text>
        <View>
          <Text style={styles.appName}>{item.app_name}</Text>
          <Text style={styles.priorityText}>Priority Rank: #{item.priority_order}</Text>
        </View>
      </View>
      
      <View style={styles.actions}>
        <View style={styles.moveButtons}>
          <TouchableOpacity 
            onPress={() => movePriority(index, 'up')} 
            style={[styles.moveBtn, index === 0 && styles.disabledBtn]}
            disabled={index === 0}
          >
            <FontAwesome name="chevron-up" size={16} color={index === 0 ? "#475569" : "#a78bfa"} />
          </TouchableOpacity>
          <TouchableOpacity 
            onPress={() => movePriority(index, 'down')} 
            style={[styles.moveBtn, index === apps.length - 1 && styles.disabledBtn]}
            disabled={index === apps.length - 1}
          >
            <FontAwesome name="chevron-down" size={16} color={index === apps.length - 1 ? "#475569" : "#a78bfa"} />
          </TouchableOpacity>
        </View>
        <Switch
          value={item.is_enabled === 1}
          onValueChange={() => toggleApp(item.app_id, item.is_enabled)}
          trackColor={{ false: "#334155", true: "#7c3aed" }}
          thumbColor={item.is_enabled === 1 ? "#fff" : "#94a3b8"}
        />
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>App Permissions</Text>
        <Text style={styles.subtitle}>Enable apps and rank their priority</Text>
      </View>
      <FlatList
        data={apps}
        renderItem={renderItem}
        keyExtractor={(item) => item.app_id.toString()}
        contentContainerStyle={styles.list}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f1a',
    paddingTop: 60,
  },
  header: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: '#e2e8f0',
  },
  subtitle: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 4,
  },
  list: {
    padding: 20,
  },
  appCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  appInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  emoji: {
    fontSize: 24,
    marginRight: 15,
  },
  appName: {
    fontSize: 16,
    fontWeight: '700',
    color: '#f8fafc',
  },
  priorityText: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 2,
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  moveButtons: {
    flexDirection: 'row',
    marginRight: 15,
  },
  moveBtn: {
    padding: 8,
    backgroundColor: 'rgba(124,58,237,0.1)',
    borderRadius: 8,
    marginHorizontal: 4,
  },
  disabledBtn: {
    backgroundColor: 'rgba(255,255,255,0.02)',
  },
});

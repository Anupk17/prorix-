import React from 'react';
import { StyleSheet, View, Text, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import FontAwesome from '@expo/vector-icons/FontAwesome';

export default function LandingScreen() {
  const router = useRouter();

  const features = [
    { icon: 'bolt', title: 'Smart Priority', desc: 'AI ranks your notifications based on your interaction habits.' },
    { icon: 'magic', title: 'AI Summaries', desc: 'Get concise bullet points of all your notifications with one click.' },
    { icon: 'tasks', title: 'Custom Ranking', desc: 'Manually prioritize your favorite apps to never miss an update.' },
    { icon: 'bar-chart', title: 'Deep Analytics', desc: 'Visualize your notification volume with colorful donut charts.' },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.smartText}>SMART</Text>
          <Text style={styles.title}>Notification Prioritizer</Text>
        </View>

        <View style={styles.infoSection}>
          <Text style={styles.sectionTitle}>Master Your Feed</Text>
          <View style={styles.featuresGrid}>
            {features.map((f, i) => (
              <View key={i} style={styles.featureCard}>
                <FontAwesome name={f.icon as any} size={24} color="#a78bfa" />
                <Text style={styles.featureTitle}>{f.title}</Text>
                <Text style={styles.featureDesc}>{f.desc}</Text>
              </View>
            ))}
          </View>
        </View>

        <View style={styles.footer}>
          <TouchableOpacity 
            style={styles.startBtn} 
            onPress={() => router.replace('/login')}
          >
            <Text style={styles.startBtnText}>Start Now</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f1a',
  },
  scrollContent: {
    padding: 20,
    alignItems: 'center',
  },
  header: {
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 20,
  },
  smartText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#a78bfa',
    letterSpacing: 4,
  },
  title: {
    fontSize: 18,
    color: '#cbd5e1',
    marginTop: 5,
  },
  illustration: {
    width: '100%',
    paddingVertical: 10,
  },
  bubbleLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  bubbleRight: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    marginBottom: 20,
  },
  circle: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.1)',
    marginHorizontal: 15,
  },
  lines: {
    gap: 8,
  },
  line: {
    height: 6,
    borderRadius: 3,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  infoSection: {
    width: '100%',
    marginVertical: 20,
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '800',
    color: '#f8fafc',
    textAlign: 'center',
    marginBottom: 20,
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  featureCard: {
    width: '48%',
    backgroundColor: 'rgba(255,255,255,0.03)',
    borderRadius: 16,
    padding: 16,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  featureTitle: {
    color: '#e2e8f0',
    fontSize: 15,
    fontWeight: '700',
    marginTop: 10,
    marginBottom: 5,
  },
  featureDesc: {
    color: '#94a3b8',
    fontSize: 12,
    lineHeight: 16,
  },
  footer: {
    width: '100%',
    marginVertical: 20,
  },
  termsTitle: {
    textAlign: 'center',
    color: '#64748b',
    fontSize: 12,
    marginBottom: 10,
    fontWeight: '600',
  },
  termsDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: '#64748b',
    alignSelf: 'center',
    marginBottom: 15,
  },
  startBtn: {
    backgroundColor: '#7c3aed',
    paddingVertical: 18,
    paddingHorizontal: 80,
    borderRadius: 16,
    marginTop: 20,
    alignSelf: 'center',
    shadowColor: '#7c3aed',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 10,
  },
  startBtnText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

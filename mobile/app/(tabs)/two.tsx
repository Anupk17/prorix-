import React, { useEffect, useState } from 'react';
import { StyleSheet, Dimensions, ScrollView } from 'react-native';
import { Text, View } from '@/components/Themed';
import { getDashboardData } from '@/services/database';
import { BarChart, PieChart } from 'react-native-chart-kit';

export default function DashboardScreen() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      let d = await getDashboardData();
      if (d.length === 0 || d.every(item => item.total_notifs === 0)) {
        // Fallback to mock data for visualization if real data is empty
        d = [
          { app_name: 'WhatsApp', total_notifs: 12, app_emoji: '💬', bandit_weight: 0.95 },
          { app_name: 'Instagram', total_notifs: 8, app_emoji: '📸', bandit_weight: 0.82 },
          { app_name: 'GPay', total_notifs: 5, app_emoji: '💳', bandit_weight: 0.75 },
          { app_name: 'Zepto', total_notifs: 4, app_emoji: '🛒', bandit_weight: 0.60 },
          { app_name: 'YouTube', total_notifs: 4, app_emoji: '▶️', bandit_weight: 0.55 },
          { app_name: 'Airtel', total_notifs: 3, app_emoji: '📶', bandit_weight: 0.45 },
          { app_name: 'Amazon', total_notifs: 2, app_emoji: '📦', bandit_weight: 0.40 },
          { app_name: 'Slack', total_notifs: 1, app_emoji: '💬', bandit_weight: 0.35 },
          { app_name: 'Gmail', total_notifs: 1, app_emoji: '📧', bandit_weight: 0.30 },
        ];
      }

      // Sort by notification volume descending
      const sortedData = [...d].sort((a, b) => (b.total_notifs || 0) - (a.total_notifs || 0));
      
      // Keep top 7 and group the rest into "Others"
      if (sortedData.length > 7) {
        const top7 = sortedData.slice(0, 7);
        const others = sortedData.slice(7);
        const othersTotal = others.reduce((sum, item) => sum + (item.total_notifs || 0), 0);
        const othersAvgWeight = others.reduce((sum, item) => sum + (item.bandit_weight || 1), 0) / others.length;
        
        setData([
          ...top7,
          {
            app_name: 'Others',
            total_notifs: othersTotal,
            app_emoji: '📦',
            bandit_weight: othersAvgWeight
          }
        ]);
      } else {
        setData(sortedData);
      }
    };
    load();
  }, []);

  const chartData = {
    labels: data.map(d => d.app_name),
    datasets: [{
      data: data.map(d => d.total_notifs || 0)
    }]
  };

  const pieData = data.map((d, i) => ({
    name: `${d.app_name} (${d.total_notifs})`,
    population: d.total_notifs || 0,
    color: ['#7c3aed', '#a78bfa', '#60a5fa', '#34d399', '#f87171', '#fbbf24'][i % 6],
    legendFontColor: '#cbd5e1',
    legendFontSize: 11
  })).filter(d => d.population > 0);

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Analytics</Text>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Volume Distribution</Text>
        {pieData.length > 0 ? (
          <View style={styles.donutContainer}>
            <PieChart
              data={pieData}
              width={Dimensions.get('window').width - 40}
              height={220}
              chartConfig={{
                color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
              }}
              accessor="population"
              backgroundColor="transparent"
              paddingLeft="15"
              absolute
              hasLegend={true}
              center={[10, 0]}
            />
            <View style={styles.donutHole} />
          </View>
        ) : (
          <Text style={styles.emptyChart}>No data available yet</Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Notification Volume</Text>
        {data.length > 0 && (
          <BarChart
            data={chartData}
            width={Dimensions.get('window').width - 40}
            height={220}
            yAxisLabel=""
            yAxisSuffix=""
            chartConfig={{
              backgroundColor: '#1e1e2d',
              backgroundGradientFrom: '#1e1e2d',
              backgroundGradientTo: '#1e1e2d',
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(167, 139, 250, ${opacity})`,
              labelColor: (opacity = 1) => `rgba(148, 163, 184, ${opacity})`,
              style: { borderRadius: 16 },
              propsForDots: { r: '6', strokeWidth: '2', stroke: '#ffa726' }
            }}
            style={{ marginVertical: 8, borderRadius: 16 }}
          />
        )}
      </View>

      <View style={styles.EngagementContainer}>
         <Text style={styles.sectionTitle}>Engagement Weights</Text>
         {data.map(d => (
           <View key={d.app_name} style={styles.weightRow}>
             <Text style={styles.weightLabel}>{d.app_emoji} {d.app_name}</Text>
             <View style={styles.barBg}>
                <View style={[styles.barFill, { width: `${Math.max(0, Math.min(100, (d.bandit_weight || 1) * 50))}%` }]} />
             </View>
             <Text style={styles.weightValue}>{(d.bandit_weight || 1).toFixed(2)}</Text>
           </View>
         ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f1a', padding: 20 },
  title: { fontSize: 24, fontWeight: '800', color: '#e2e8f0', marginTop: 40, marginBottom: 20 },
  section: { marginBottom: 30 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: '#a78bfa', marginBottom: 15 },
  EngagementContainer: { backgroundColor: 'rgba(255,255,255,0.03)', padding: 20, borderRadius: 20, marginBottom: 40 },
  weightRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 15 },
  weightLabel: { width: 100, color: '#cbd5e1', fontSize: 14 },
  barBg: { flex: 1, height: 8, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 4, marginHorizontal: 10, overflow: 'hidden' },
  barFill: { height: '100%', backgroundColor: '#7c3aed' },
  weightValue: { width: 40, color: '#a78bfa', fontSize: 12, fontWeight: '600', textAlign: 'right' },
  donutContainer: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255,255,255,0.02)',
    borderRadius: 20,
    paddingVertical: 10,
  },
  donutHole: {
    position: 'absolute',
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#0f0f1a',
    left: '23%', // Adjusted for center offset
    top: '32%',
  },
  emptyChart: {
    color: '#64748b',
    textAlign: 'center',
    padding: 40,
    fontSize: 14,
    fontStyle: 'italic',
  }
});

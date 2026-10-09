import { useEffect, useState } from 'react';
import { ScrollView, Text, View } from 'react-native';

import { errorMessage } from '../api/errors';
import {
  deleteDeviceToken,
  listDeviceTokens,
  registerDeviceToken,
} from '../api/resources';
import type { DeviceToken } from '../api/types';
import { sessionNotices, useSessionNotices } from '../notices';
import {
  ErrorText,
  Field,
  LinkButton,
  Note,
  PrimaryButton,
  styles,
} from '../ui';

export function NotificationsScreen() {
  const notices = useSessionNotices();
  const [tokens, setTokens] = useState<DeviceToken[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tokenText, setTokenText] = useState('');
  const [platform, setPlatform] = useState<'android' | 'ios'>('android');
  const [pending, setPending] = useState(false);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    listDeviceTokens()
      .then(page => {
        if (!cancelled) {
          setTokens(page.device_tokens);
        }
      })
      .catch((caught: unknown) => {
        if (!cancelled) {
          setTokens([]);
          setError(errorMessage(caught));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [reload]);

  async function onRegister() {
    const token = tokenText.trim();
    if (!token) {
      setError(
        'Enter a device token. This screen does not create an FCM token.',
      );
      return;
    }
    setPending(true);
    setError(null);
    try {
      await registerDeviceToken(token, platform);
      setTokenText('');
      sessionNotices.add('Registered a device token for this account.');
      setReload(value => value + 1);
    } catch (caught) {
      setError(errorMessage(caught));
    } finally {
      setPending(false);
    }
  }

  async function onDelete(tokenId: string) {
    setError(null);
    try {
      await deleteDeviceToken(tokenId);
      sessionNotices.add('Removed a device token from this account.');
      setReload(value => value + 1);
    } catch (caught) {
      setError(errorMessage(caught));
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.screen}>
      <Text style={styles.title}>Notifications</Text>
      <Note>
        There is no notification inbox endpoint. Device tokens below come from
        GET /api/v1/device-tokens. Session notes are kept in this app only.
        Email and push on the server stay mocks. This screen does not use FCM.
      </Note>
      <ErrorText message={error} />
      <Text style={styles.body}>Device tokens</Text>
      {tokens === null ? (
        <Text style={styles.body}>Loading tokens…</Text>
      ) : null}
      {tokens !== null && tokens.length === 0 ? (
        <Text style={styles.note}>
          No device token is stored for this account.
        </Text>
      ) : null}
      {tokens?.map(row => (
        <View key={row.id} style={styles.card}>
          <Text style={styles.body}>
            {row.platform} · {row.token}
          </Text>
          <Text style={styles.note}>{row.created_at}</Text>
          <LinkButton
            label="Remove token"
            onPress={() => {
              onDelete(row.id).catch(() => undefined);
            }}
          />
        </View>
      ))}
      <Field
        label="Device token"
        onChangeText={setTokenText}
        value={tokenText}
      />
      <View style={styles.row}>
        <PrimaryButton
          label={platform === 'android' ? 'Android selected' : 'Use Android'}
          onPress={() => setPlatform('android')}
        />
        <PrimaryButton
          label={platform === 'ios' ? 'iOS selected' : 'Use iOS'}
          onPress={() => setPlatform('ios')}
        />
      </View>
      <PrimaryButton
        disabled={pending}
        label={pending ? 'Saving token…' : 'Save device token'}
        onPress={() => {
          onRegister().catch(() => undefined);
        }}
      />
      <Text style={styles.body}>Session notes</Text>
      {notices.length === 0 ? (
        <Text style={styles.note}>No session notes yet.</Text>
      ) : (
        notices.map(notice => (
          <Text key={notice.id} style={styles.note}>
            {notice.text}
          </Text>
        ))
      )}
    </ScrollView>
  );
}

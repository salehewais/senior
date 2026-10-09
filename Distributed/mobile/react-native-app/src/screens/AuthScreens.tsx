import { useState } from 'react';
import { Text, View } from 'react-native';

import { errorMessage } from '../api/errors';
import { loginAccount, registerAccount } from '../api/resources';
import { sessionNotices } from '../notices';
import { ErrorText, Field, LinkButton, PrimaryButton, styles } from '../ui';

export function LoginScreen({
  onRegister,
  onLoggedIn,
}: {
  onRegister: () => void;
  onLoggedIn: () => void;
}) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit() {
    setPending(true);
    setError(null);
    try {
      await loginAccount(email.trim(), password);
      sessionNotices.add('Signed in.');
      onLoggedIn();
    } catch (caught) {
      setError(errorMessage(caught));
      setPending(false);
    }
  }

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Sign in</Text>
      <ErrorText message={error} />
      <Field label="Email" onChangeText={setEmail} value={email} />
      <Field
        label="Password"
        onChangeText={setPassword}
        secureTextEntry
        value={password}
      />
      <PrimaryButton
        disabled={pending}
        label={pending ? 'Signing in…' : 'Sign in'}
        onPress={() => {
          onSubmit().catch(() => undefined);
        }}
      />
      <LinkButton label="Create an account" onPress={onRegister} />
    </View>
  );
}

export function RegisterScreen({
  onSignIn,
  onRegistered,
}: {
  onSignIn: () => void;
  onRegistered: () => void;
}) {
  const [email, setEmail] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit() {
    setPending(true);
    setError(null);
    try {
      await registerAccount(email.trim(), displayName.trim(), password);
      sessionNotices.add('Signed in.');
      onRegistered();
    } catch (caught) {
      setError(errorMessage(caught));
      setPending(false);
    }
  }

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Create an account</Text>
      <ErrorText message={error} />
      <Field label="Email" onChangeText={setEmail} value={email} />
      <Field
        label="Display name"
        onChangeText={setDisplayName}
        value={displayName}
      />
      <Field
        label="Password"
        onChangeText={setPassword}
        secureTextEntry
        value={password}
      />
      <PrimaryButton
        disabled={pending}
        label={pending ? 'Creating account…' : 'Create account'}
        onPress={() => {
          onSubmit().catch(() => undefined);
        }}
      />
      <LinkButton label="Sign in" onPress={onSignIn} />
    </View>
  );
}

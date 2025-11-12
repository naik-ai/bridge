/**
 * Home Page
 *
 * Redirects to dashboards gallery.
 */

import { redirect } from 'next/navigation';

export default function HomePage() {
  redirect('/dashboards');
}

import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatButtonModule } from '@angular/material/button';

interface MenuItem {
  icon: string;
  label: string;
  route: string;
  children?: MenuItem[];
  isOpen?: boolean;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatIconModule,
    MatListModule,
    MatButtonModule
  ],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css']
})
export class SidebarComponent {
  @Input() isSidebarCollapsed = false;
  @Output() sidebarToggle = new EventEmitter<void>();

  menuItems: MenuItem[] = [
    {
      icon: 'dashboard',
      label: 'Dashboard',
      route: '/dashboard'
    },
    {
      icon: 'tower',
      label: 'Tower Instances',
      route: '/tower-instances'
    },
    {
      icon: 'security',
      label: 'Credential Types',
      route: '/credential-types'
    },
    {
      icon: 'settings',
      label: 'Execution Environments',
      route: '/execution-environments'
    },
    {
      icon: 'analytics',
      label: 'Statistics',
      route: '/statistics'
    },
    {
      icon: 'history',
      label: 'Audit Logs',
      route: '/audit-logs'
    }
  ];

  toggleSidebar() {
    this.sidebarToggle.emit();
  }

  onMenuItemClick(item: MenuItem) {
    // Handle menu item click if needed
    console.log('Menu item clicked:', item.label);
  }
}

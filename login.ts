import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  username = '';
  password = '';

  constructor(private router: Router) {}

  login() {
    // for now just simple validation
    if (this.username && this.password) {
      this.router.navigate(['/dashboard']);
    } else {
      alert('Please enter username and password');
    }
  }
}
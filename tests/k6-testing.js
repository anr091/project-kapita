import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "10s", target: 50 },
    { duration: "20s", target: 50 },
    { duration: "5s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(90) < 1000"], // 90% harus di bawah 1000ms
    checks: ["rate>0.99"], // gagal kurang dari 1%
    http_req_failed: ["rate < 0.01"],
    iterations: ["rate > 20"], // 10 iterasi/detik
  },
};

export default function () {
  const res = http.get("http://127.0.0.1:5000", {
    cookies: {
      token:
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiSmhvbm55Iiwicm9sZSI6IlIwMDEiLCJyb2xlTmFtZSI6IkFkbWluIiwicm9sZVBlcm0iOnsicmV0YWlsIGFuZCBzaGlwbWVudCI6dHJ1ZSwiYWNjb3VudCBtYW5hZ2VtZW50Ijp0cnVlLCJyZXBvcnQgZGF0YSI6dHJ1ZSwic3RvY2sgbWFuYWdlbWVudCI6dHJ1ZX0sImlkIjoiUDIwMjUwMDgiLCJmaXJzdExvZ29uIjpmYWxzZSwiZXhwIjoxNzY1NDU2ODU3LCJpYXQiOjE3NjU0MTM2NTd9.ng9k6-TuPdVqJeVt-NujiA67TIxNhv4pPBAx7jw2BR0",
    },
  });
  const api = http.get("http://127.0.0.1:5000/api/product", {
    cookies: {
      token:
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiSmhvbm55Iiwicm9sZSI6IlIwMDEiLCJyb2xlTmFtZSI6IkFkbWluIiwicm9sZVBlcm0iOnsicmV0YWlsIGFuZCBzaGlwbWVudCI6dHJ1ZSwiYWNjb3VudCBtYW5hZ2VtZW50Ijp0cnVlLCJyZXBvcnQgZGF0YSI6dHJ1ZSwic3RvY2sgbWFuYWdlbWVudCI6dHJ1ZX0sImlkIjoiUDIwMjUwMDgiLCJmaXJzdExvZ29uIjpmYWxzZSwiZXhwIjoxNzY1NDU2ODU3LCJpYXQiOjE3NjU0MTM2NTd9.ng9k6-TuPdVqJeVt-NujiA67TIxNhv4pPBAx7jw2BR0",
    },
  });
  check(res, {
    "statusnya 200 (ok)": (r) => r.status == 200,
    "respons time < 1000ms": (r) => r.timings.duration < 1000,
    "body isinya teks ini": (r) =>
      r.body && r.body.includes("Hello! Jhonny As Admin"),
    "tidak ditendang ke login page (status xhrnya < 300)": (r) =>
      r.status < 300,
  });
  check(api, {
    "api statusnya 200 (ok)": (r) => r.status == 200,
    "api respon time < 1000ms": (r) => r.timings.duration < 1000,
    "ukuran respon masuk akal": (r) =>
      r.body && r.body.length > 100 && r.body.length < 10000,
  });
  sleep(1);
}

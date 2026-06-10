import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

const protectedPaths = ["/dashboard", "/reminders", "/team", "/settings", "/admin"]
const authPaths = ["/auth/login", "/auth/register", "/auth/forgot-password"]
const adminPaths = ["/admin"]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const token = request.cookies.get("access_token")?.value

  const isProtected = protectedPaths.some((path) => pathname.startsWith(path))
  const isAuth = authPaths.some((path) => pathname.startsWith(path))
  const isAdmin = adminPaths.some((path) => pathname.startsWith(path))

  if (isProtected && !token) {
    const loginUrl = new URL("/auth/login", request.url)
    loginUrl.searchParams.set("redirect", pathname)
    return NextResponse.redirect(loginUrl)
  }

  if (isAdmin && token) {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]))
      if (payload.role !== "superuser" && payload.role !== "admin") {
        return NextResponse.redirect(new URL("/dashboard", request.url))
      }
    } catch {
      return NextResponse.redirect(new URL("/auth/login", request.url))
    }
  }

  if (isAuth && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico|manifest.json|robots.txt).*)",
  ],
}

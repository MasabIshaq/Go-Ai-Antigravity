/**
 * Go Ai — auth validation (Java).
 * Compile: javac GoAiAuth.java
 * Run:     java GoAiAuth validate email@x.com mypassword
 */
import java.util.regex.Pattern;

public class GoAiAuth {
    private static final Pattern EMAIL = Pattern.compile("^[\\w.+-]+@[\\w.-]+\\.\\w+$");
    private static final Pattern USERNAME = Pattern.compile("^[a-zA-Z0-9_]{3,24}$");

    public static boolean isValidEmail(String email) {
        return email != null && EMAIL.matcher(email.trim()).matches();
    }

    public static boolean isValidUsername(String username) {
        return username != null && USERNAME.matcher(username.trim()).matches();
    }

    public static String validatePassword(String password) {
        if (password == null || password.length() < 6) {
            return "Password must be at least 6 characters";
        }
        return null;
    }

    public static void main(String[] args) {
        if (args.length < 2 || !"validate".equals(args[0])) {
            System.out.println("Usage: java GoAiAuth validate <email> <password> [username]");
            return;
        }
        String email = args[1];
        String password = args.length > 2 ? args[2] : "";
        String username = args.length > 3 ? args[3] : "user";

        boolean ok = isValidEmail(email) && validatePassword(password) == null;
        if (args.length > 3) {
            ok = ok && isValidUsername(username);
        }
        System.out.println(ok ? "OK" : "INVALID");
        System.exit(ok ? 0 : 1);
    }
}

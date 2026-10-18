using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Reflection;
using System.Windows.Forms;

namespace MinuteCat
{
    internal static class Program
    {
        [STAThread]
        private static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            try
            {
                Application.Run(new ControlWindow());
            }
            catch (Exception error)
            {
                MessageBox.Show(error.Message, "Minute Cat", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }

    internal sealed class ControlWindow : Form
    {
        private static readonly string[] Styles = {
            "Orange tabby", "Tuxedo", "Black cat", "Calico", "Silver tabby", "Siamese"
        };

        private readonly Bitmap[,] sprites = new Bitmap[6, 2];
        private readonly CatWindow catWindow = new CatWindow();
        private readonly Timer reminder = new Timer { Interval = 60000 };
        private readonly Timer animation = new Timer { Interval = 33 };
        private readonly ComboBox styleChoice = new ComboBox();
        private readonly Button pauseButton = new Button();
        private readonly Label status = new Label();
        private DateTime walkStarted;
        private int nextStyle;
        private int currentStyle;
        private bool paused;

        public ControlWindow()
        {
            Text = "Minute Cat";
            ClientSize = new Size(302, 187);
            FormBorderStyle = FormBorderStyle.FixedDialog;
            MaximizeBox = false;
            StartPosition = FormStartPosition.Manual;
            Location = new Point(20, 20);
            BackColor = Color.FromArgb(255, 245, 233);
            Font = new Font("Segoe UI", 9);

            AddLabel("Minute Cat", 16, 12, 220, 29, FontStyle.Bold, 15);
            AddLabel("A tiny walk, every minute.", 17, 43, 260, 23);
            AddLabel("Cat style", 17, 76, 75, 24);
            styleChoice.Location = new Point(95, 73);
            styleChoice.Size = new Size(189, 25);
            styleChoice.DropDownStyle = ComboBoxStyle.DropDownList;
            styleChoice.Items.Add("Surprise me");
            styleChoice.Items.AddRange(Styles);
            styleChoice.SelectedIndex = 0;
            Controls.Add(styleChoice);

            status.Location = new Point(17, 112);
            status.Size = new Size(270, 22);
            status.Text = "Walking every minute";
            Controls.Add(status);

            var showButton = AddButton("Show now", 16, 143, 85);
            showButton.Click += (sender, args) => ShowCat();
            pauseButton.Text = "Pause";
            pauseButton.Location = new Point(108, 143);
            pauseButton.Size = new Size(79, 30);
            pauseButton.Click += (sender, args) => TogglePause();
            Controls.Add(pauseButton);
            var quitButton = AddButton("Quit", 194, 143, 90);
            quitButton.Click += (sender, args) => Close();

            LoadSprites();
            reminder.Tick += (sender, args) => ShowCat();
            animation.Tick += (sender, args) => Animate();
            Shown += (sender, args) => ShowCat();
        }

        private void AddLabel(string value, int x, int y, int width, int height,
            FontStyle style = FontStyle.Regular, float size = 9)
        {
            var label = new Label {
                Text = value,
                Location = new Point(x, y),
                Size = new Size(width, height),
                Font = new Font("Segoe UI", size, style)
            };
            Controls.Add(label);
        }

        private Button AddButton(string value, int x, int y, int width)
        {
            var button = new Button {
                Text = value,
                Location = new Point(x, y),
                Size = new Size(width, 30)
            };
            Controls.Add(button);
            return button;
        }

        private void LoadSprites()
        {
            var assembly = Assembly.GetExecutingAssembly();
            for (int pose = 0; pose < 2; pose++)
            {
                string resource = pose == 0 ? "MinuteCat.cats_walk_a.png" : "MinuteCat.cats_walk_b.png";
                using (var stream = assembly.GetManifestResourceStream(resource))
                {
                    if (stream == null) throw new InvalidOperationException("Cat artwork is missing.");
                    using (var sheet = new Bitmap(stream))
                    {
                        if (sheet.Width != 1536 || sheet.Height != 1024)
                            throw new InvalidOperationException("Cat artwork has an unexpected size.");
                        for (int style = 0; style < Styles.Length; style++)
                        {
                            var sprite = new Bitmap(171, 171);
                            using (var graphics = Graphics.FromImage(sprite))
                            {
                                graphics.InterpolationMode = InterpolationMode.HighQualityBicubic;
                                graphics.DrawImage(sheet, new Rectangle(0, 0, 171, 171),
                                    new Rectangle((style % 3) * 512, (style / 3) * 512, 512, 512),
                                    GraphicsUnit.Pixel);
                            }
                            sprites[style, pose] = sprite;
                        }
                    }
                }
            }
        }

        private void ShowCat()
        {
            animation.Stop();
            catWindow.Hide();
            currentStyle = styleChoice.SelectedIndex == 0 ? nextStyle++ % Styles.Length : styleChoice.SelectedIndex - 1;
            catWindow.SetCat(sprites[currentStyle, 0], Styles[currentStyle]);
            walkStarted = DateTime.UtcNow;
            PlaceCat(0);
            catWindow.Show();
            catWindow.BringToFront();
            animation.Start();
            reminder.Stop();
            if (!paused) reminder.Start();
        }

        private void Animate()
        {
            double elapsed = (DateTime.UtcNow - walkStarted).TotalSeconds;
            if (elapsed >= 10)
            {
                animation.Stop();
                catWindow.Hide();
                return;
            }
            PlaceCat(elapsed / 10);
            catWindow.SetCat(sprites[currentStyle, (int)(elapsed * 6) % 2], Styles[currentStyle]);
        }

        private void PlaceCat(double progress)
        {
            Rectangle screen = Screen.PrimaryScreen.Bounds;
            int x = screen.Left + (int)Math.Round((screen.Width - catWindow.Width) * (1 - progress));
            double elapsed = (DateTime.UtcNow - walkStarted).TotalSeconds;
            int y = screen.Bottom - catWindow.Height - 20 + (int)Math.Round(Math.Abs(Math.Sin(elapsed * 14)) * 3);
            catWindow.Location = new Point(x, y);
        }

        private void TogglePause()
        {
            paused = !paused;
            reminder.Stop();
            if (paused)
            {
                animation.Stop();
                catWindow.Hide();
            }
            else
            {
                reminder.Start();
            }
            pauseButton.Text = paused ? "Resume" : "Pause";
            status.Text = paused ? "Paused — show a cat any time" : "Walking every minute";
        }

        protected override void OnFormClosed(FormClosedEventArgs args)
        {
            reminder.Stop();
            animation.Stop();
            catWindow.Close();
            foreach (var sprite in sprites)
                if (sprite != null) sprite.Dispose();
            base.OnFormClosed(args);
        }
    }

    internal sealed class CatWindow : Form
    {
        private readonly Timer heartTimer = new Timer { Interval = 900 };
        private Bitmap sprite;
        private string catName;
        private bool showHeart;

        public CatWindow()
        {
            FormBorderStyle = FormBorderStyle.None;
            ShowInTaskbar = false;
            TopMost = true;
            ClientSize = new Size(200, 210);
            BackColor = Color.FromArgb(255, 245, 233);
            TransparencyKey = BackColor;
            DoubleBuffered = true;
            heartTimer.Tick += (sender, args) => {
                heartTimer.Stop();
                showHeart = false;
                Invalidate();
            };
            Click += (sender, args) => {
                showHeart = true;
                heartTimer.Stop();
                heartTimer.Start();
                Invalidate();
            };
        }

        public void SetCat(Bitmap image, string name)
        {
            sprite = image;
            catName = name;
            Invalidate();
        }

        protected override void OnPaint(PaintEventArgs args)
        {
            base.OnPaint(args);
            if (sprite == null) return;
            args.Graphics.DrawImageUnscaled(sprite, 14, 4);
            using (var font = new Font("Segoe UI", 10, FontStyle.Bold))
            using (var brush = new SolidBrush(Color.FromArgb(81, 65, 58)))
            using (var format = new StringFormat { Alignment = StringAlignment.Center })
                args.Graphics.DrawString(catName, font, brush, new RectangleF(0, 185, 200, 24), format);
            if (showHeart)
            {
                using (var font = new Font("Segoe UI Symbol", 23, FontStyle.Bold))
                using (var brush = new SolidBrush(Color.FromArgb(229, 120, 140)))
                    args.Graphics.DrawString("♥", font, brush, 55, 5);
            }
        }
    }
}

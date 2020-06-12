package main
import ("fmt"
	"os"
	"path/filepath")

func main() {
	FullFilename, _ := filepath.Abs(os.Args[1])
	fmt.Println(filepath.Dir(filepath.Dir(FullFilename) + "/../"))
}